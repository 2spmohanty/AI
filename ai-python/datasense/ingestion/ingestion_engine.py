"""
ingestion/ingestion_engine.py

CLI entry point for a single ingestion run, targeting exactly one dataset.

Usage:
    uv run python -m datasense.ingestion.ingestion_engine \\
        --dataset transaction \\
        --rows 1000 \\
        --error_pct 15 \\
        --error_type null_spike

Flow:
    1. Fetch dataset contract from Neo4j (schema_registry)
    2. If the dataset has a FK, sample a random DQ_PASSED upstream partition
       (or an explicit --source-execution-id override) and read its PK values
    3. start_run() -> load_runs row at ingestion_status=INITIATED
    4. mark_running()
    5. generate_rows() -> clean, contract-valid rows
    6. inject_anomaly() if --error_type given -> mutates rows
    7. Write partitioned file to disk (CSV or JSON per contract file_format)
    8. mark_ingestion_success()
    9. record_injection() into ground_truth.db (ALWAYS — clean runs too)
   10. publish MQTT event on pipeline/ingestion/complete
"""

import argparse
import csv
import json
import os
import uuid
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from datasense.metadata.schema_registry import get_dataset_schema
from datasense.ingestion.generator import generate_rows, inject_anomaly, ANOMALY_REGISTRY
from datasense.storage import load_runs_db, ground_truth_db
from datasense.storage.paths import INBOUND_DIR
from datasense.common import console
from datasense.common.mqtt_client import publish_message
from datasense.common.topics import INGESTION_COMPLETE

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "infra", ".env"))

# Internal contract name -> output directory name. Deliberately asymmetric
# (customer stays singular, accounts/transactions pluralize) to match the
# directory convention specified in the project brief exactly.
DIR_NAME_MAP = {"customer": "customer", "account": "accounts", "transaction": "transactions"}

# child dataset -> (parent dataset, FK column on child, PK column on parent)
FK_LINEAGE = {
    "account": ("customer", "customer_id", "customer_id"),
    "transaction": ("account", "account_id", "account_id"),
}


def build_output_path(dataset_name: str, dt: datetime) -> Path:
    dir_name = DIR_NAME_MAP[dataset_name]
    year, month, day = f"{dt.year:04d}", f"{dt.month:02d}", f"{dt.day:02d}"

    if dataset_name == "transaction":
        hms = dt.strftime("%H-%M-%S")
        random_id = uuid.uuid4().hex[:8]
        return (INBOUND_DIR / dir_name / f"year={year}" / f"month={month}"
                / f"day={day}" / hms / f"{dataset_name}_{random_id}.json")

    timestamp = dt.strftime("%Y%m%dT%H%M%S")
    return (INBOUND_DIR / dir_name / f"year={year}" / f"month={month}"
             / f"day={day}" / f"{dataset_name}_{timestamp}.csv")


def read_pk_values(file_path: str, file_format: str, pk_column: str) -> list:
    path = Path(file_path)
    if file_format == "csv":
        with open(path, "r", newline="") as f:
            reader = csv.DictReader(f)
            return [row[pk_column] for row in reader if row.get(pk_column)]
    elif file_format == "json":
        with open(path, "r") as f:
            data = json.load(f)
            return [row[pk_column] for row in data if row.get(pk_column)]
    else:
        raise ValueError(f"Unsupported file_format: {file_format}")


def write_rows(rows: list[dict], output_path: Path, file_format: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if file_format == "csv":
        if not rows:
            raise ValueError("Cannot write an empty CSV — no rows to derive headers from")
        fieldnames = list(rows[0].keys())
        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    elif file_format == "json":
        with open(output_path, "w") as f:
            json.dump(rows, f, indent=2, default=str)
    else:
        raise ValueError(f"Unsupported file_format: {file_format}")


def resolve_fk_pool(dataset_name: str, source_execution_id: str = None) -> tuple[list, str]:
    """
    Returns (fk_pool_values, upstream_execution_id). Raises if the dataset
    needs a FK pool but no eligible upstream partition exists — that's a
    build-order problem the user needs to fix (ingest the parent first).
    """
    parent_dataset, _, parent_pk_column = FK_LINEAGE[dataset_name]

    if source_execution_id:
        upstream_run = load_runs_db.get_run_by_id_or_raise(source_execution_id)
    else:
        upstream_run = load_runs_db.get_random_dq_passed_partition(parent_dataset)
        if upstream_run is None:
            raise RuntimeError(
                f"No DQ_PASSED '{parent_dataset}' partition found. "
                f"Ingest '{parent_dataset}' first (with error_pct=0) before ingesting '{dataset_name}'."
            )

    parent_schema = get_dataset_schema(parent_dataset)
    values = read_pk_values(upstream_run["file_path"], parent_schema.file_format, parent_pk_column)
    if not values:
        raise RuntimeError(
            f"Upstream partition {upstream_run['file_path']} contains no usable "
            f"'{parent_pk_column}' values."
        )
    return values, upstream_run["execution_id"]


def run_ingestion(
    dataset: str,
    rows: int,
    error_pct: float = 0.0,
    error_type: str = None,
    error_column: str = None,
    seed: int = None,
    source_execution_id: str = None,
    is_cascade_origin: bool = False,
    resolves_ground_truth_id: str = None,
    scenario_id: str = None,
    scenario_step: int = None,
) -> str:
    """
    Callable core of a single ingestion run. Used by both main() (CLI) and
    pipeline_orchestrator.py (scripted scenarios), so the two never drift out
    of sync with each other. Returns the generated execution_id.
    """
    load_runs_db.init_db()
    ground_truth_db.init_db()

    schema = get_dataset_schema(dataset)
    now = datetime.now()
    output_path = build_output_path(dataset, now)

    fk_pool, upstream_execution_id = None, None
    if dataset in FK_LINEAGE:
        console.log_info(f"Resolving FK pool for '{dataset}' from upstream partition...")
        fk_pool, upstream_execution_id = resolve_fk_pool(dataset, source_execution_id)
        console.log_info(f"Sampled {len(fk_pool)} FK values from upstream execution_id={upstream_execution_id}")

    partition_date = now.strftime("%Y-%m-%d")
    execution_id = load_runs_db.start_run(dataset, partition_date, str(output_path))
    console.log_info(f"Run started: {execution_id} (ingestion_status=INITIATED)")

    try:
        load_runs_db.mark_running(execution_id)

        generated_rows = generate_rows(dataset, schema, rows, fk_pool)

        injection_result = None
        if error_type:
            injection_result = inject_anomaly(
                error_type, generated_rows, schema,
                error_pct=error_pct, target_column=error_column, seed=seed,
            )
            generated_rows = injection_result.rows

        write_rows(generated_rows, output_path, schema.file_format)
        final_row_count = len(generated_rows)

        load_runs_db.mark_ingestion_success(execution_id, row_count=final_row_count)

        if injection_result:
            ground_truth_db.record_injection(
                execution_id=execution_id,
                tier=injection_result.tier,
                error_type=injection_result.error_type,
                dataset=dataset,
                target_column=injection_result.target_column,
                requested_error_pct=error_pct,
                actual_rows_affected=injection_result.actual_rows_affected,
                upstream_execution_id=upstream_execution_id,
                is_cascade_origin=is_cascade_origin,
                resolves_ground_truth_id=resolves_ground_truth_id,
                description=injection_result.description,
                scenario_id=scenario_id,
                scenario_step=scenario_step,
            )
            injection_summary = f"{injection_result.error_type} (tier {injection_result.tier}) -> {injection_result.description}"
        else:
            ground_truth_db.record_injection(
                execution_id=execution_id,
                tier=0,
                error_type="clean",
                dataset=dataset,
                requested_error_pct=0.0,
                actual_rows_affected=0,
                upstream_execution_id=upstream_execution_id,
                is_cascade_origin=False,
                resolves_ground_truth_id=resolves_ground_truth_id,
                description="Clean ingestion, no anomaly injected"
                             if resolves_ground_truth_id is None
                             else "Clean ingestion — resolves a prior failure (silent recovery)",
                scenario_id=scenario_id,
                scenario_step=scenario_step,
            )
            injection_summary = None

        console.log_run_summary(execution_id, dataset, str(output_path),
                                 final_row_count, injection_summary)

        publish_message(INGESTION_COMPLETE, {"execution_id": execution_id, "dataset": dataset})
        console.log_success(f"Published to '{INGESTION_COMPLETE}'")

        return execution_id

    except Exception as e:
        load_runs_db.mark_ingestion_failed(execution_id, remarks=str(e))
        console.log_error(f"Ingestion failed for {execution_id}: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(description="DataSense ingestion engine")
    parser.add_argument("--dataset", required=True, choices=["customer", "account", "transaction"])
    parser.add_argument("--rows", type=int, default=1000)
    parser.add_argument("--error_pct", type=float, default=0.0)
    parser.add_argument("--error_type", choices=list(ANOMALY_REGISTRY), default=None)
    parser.add_argument("--error_column", default=None,
                         help="Force a specific target column; omit to pick randomly among eligible columns")
    parser.add_argument("--seed", type=int, default=None,
                         help="Seed anomaly injection randomness for reproducibility")
    parser.add_argument("--source-execution-id", default=None,
                         help="Pin FK sampling to a specific upstream execution_id instead of random")
    parser.add_argument("--is-cascade-origin", action="store_true",
                         help="Mark this injection as the true root cause in a multi-run scenario")
    parser.add_argument("--scenario-id", default=None,
                         help="Group this run under a cascade scenario (set by pipeline_orchestrator.py)")
    parser.add_argument("--scenario-step", type=int, default=None)
    args = parser.parse_args()

    run_ingestion(
        dataset=args.dataset,
        rows=args.rows,
        error_pct=args.error_pct,
        error_type=args.error_type,
        error_column=args.error_column,
        seed=args.seed,
        source_execution_id=args.source_execution_id,
        is_cascade_origin=args.is_cascade_origin,
        scenario_id=args.scenario_id,
        scenario_step=args.scenario_step,
    )


if __name__ == "__main__":
    main()