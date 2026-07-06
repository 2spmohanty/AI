"""
dq/dq_pipeline.py

Persistent worker process. Run this in its own terminal, alongside
ingestion_engine.py runs in another. Subscribes to 'pipeline/ingestion/complete',
looks up the run in load_runs.db, compares the physical file's schema against
the Neo4j contract, and — only if schema matches — runs a Great Expectations
checkpoint built from the contract's declared constraints.

Usage:
    uv run python -m datasense.dq.dq_pipeline
"""

import json
import os

import great_expectations as ge
import pandas as pd
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

from datasense.metadata.schema_registry import get_dataset_schema, DatasetSchema
from datasense.storage import load_runs_db
from datasense.common import console
from datasense.common.mqtt_client import publish_message
from datasense.common.topics import INGESTION_COMPLETE, ANOMALY_ALERT

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "infra", ".env"))


def load_dataframe(file_path: str, file_format: str) -> pd.DataFrame:
    """
    CSV: pd.read_csv is fine as-is — CSV has no native type distinction to
    preserve, so pandas' inference is the only option anyway.

    JSON: deliberately NOT pd.read_json(). Pandas' JSON reader applies its
    own type-coercion pass (convert_axes / _try_convert_data) that silently
    converts numeric-looking strings back into floats — which defeats
    schema_type_change detection, since the whole point of that injection is
    a genuinely-quoted "123.45" vs a bare 123.45. Loading via json.load() and
    building the DataFrame directly from the raw records preserves the true
    Python type per value (str stays str, float stays float), so a column
    that's actually all strings correctly becomes dtype=object.
    """
    if file_format == "csv":
        return pd.read_csv(file_path)
    elif file_format == "json":
        with open(file_path, "r") as f:
            records = json.load(f)
        return pd.DataFrame(records)
    else:
        raise ValueError(f"Unsupported file_format: {file_format}")


# ---------------------------------------------------------------------------
# Schema comparison — runs BEFORE any GE checkpoint. If this fails, GE never
# runs at all, per the original design: schema drift is a structural failure,
# checking value constraints on a structurally wrong file is meaningless.
# ---------------------------------------------------------------------------

def _infer_category(dtype) -> str:
    if pd.api.types.is_bool_dtype(dtype):
        return "boolean"
    if pd.api.types.is_numeric_dtype(dtype):
        return "numeric"
    return "string"


EXPECTED_CATEGORY = {
    "STRING": "string", "DATE": "string", "DATETIME": "string",
    "INTEGER": "numeric", "FLOAT": "numeric", "BOOLEAN": "boolean",
}


def compare_schema(df: pd.DataFrame, schema: DatasetSchema) -> tuple[bool, str]:
    expected_columns = {c.name: c.data_type for c in schema.columns}
    actual_columns = set(df.columns)

    missing = set(expected_columns.keys()) - actual_columns
    extra = actual_columns - set(expected_columns.keys())
    if missing or extra:
        parts = []
        if missing:
            parts.append(f"missing columns {sorted(missing)}")
        if extra:
            parts.append(f"unexpected columns {sorted(extra)}")
        return False, "Schema drift: " + ", ".join(parts)

    type_mismatches = []
    for col_name, expected_type in expected_columns.items():
        actual_category = _infer_category(df[col_name].dtype)
        expected_category = EXPECTED_CATEGORY[expected_type]
        if actual_category != expected_category:
            type_mismatches.append(
                f"'{col_name}' expected {expected_category} ({expected_type}), "
                f"found {actual_category} ({df[col_name].dtype})"
            )
    if type_mismatches:
        return False, "Schema drift: " + "; ".join(type_mismatches)

    return True, ""


# ---------------------------------------------------------------------------
# Referential integrity — genuinely missing before. GE's column-level checks
# (non-null, categorical, range) cannot catch "this FK value doesn't exist in
# the parent dataset" because that requires a cross-dataset join, not a
# single-column constraint. This runs after schema comparison (no point
# joining on a column that doesn't structurally exist) and before GE.
# ---------------------------------------------------------------------------

def get_valid_parent_ids(parent_dataset: str, parent_pk_column: str) -> set:
    """
    Union of PK values across EVERY DQ_PASSED partition of the parent
    dataset — not just the one this run's FK values happened to be sampled
    from. A FK value is only genuinely orphaned if it doesn't exist in ANY
    known-good parent data, matching what a real referential integrity check
    against a live parent table would see.
    """
    parent_schema = get_dataset_schema(parent_dataset)
    valid_ids = set()
    for run in load_runs_db.get_all_dq_passed_runs(parent_dataset):
        df = load_dataframe(run["file_path"], parent_schema.file_format)
        if parent_pk_column in df.columns:
            valid_ids.update(df[parent_pk_column].astype(str).tolist())
    return valid_ids


def check_referential_integrity(df: pd.DataFrame, schema: DatasetSchema) -> tuple[bool, str]:
    fk_columns = [c for c in schema.columns if c.is_foreign_key and c.references]
    if not fk_columns:
        return True, ""

    failures = []
    for col in fk_columns:
        parent_dataset, parent_pk_column = col.references.split(".")
        valid_ids = get_valid_parent_ids(parent_dataset, parent_pk_column)
        if not valid_ids:
            # No DQ_PASSED parent partitions exist at all yet — can't validate
            # against an empty universe, so skip rather than fail everything.
            continue
        actual_values = df[col.name].astype(str)
        orphan_mask = ~actual_values.isin(valid_ids)
        orphan_count = int(orphan_mask.sum())
        if orphan_count > 0:
            failures.append(
                f"'{col.name}' has {orphan_count}/{len(df)} row(s) referencing "
                f"non-existent {col.references} (orphaned, no matching parent)"
            )

    if failures:
        return False, "; ".join(failures)
    return True, ""


# ---------------------------------------------------------------------------
# Great Expectations checkpoint — built dynamically from the Neo4j contract.
# Uses the legacy ge.dataset.PandasDataset API (stable across 0.18.x) rather
# than the newer Fluent/context API, which churns more across versions.
# ---------------------------------------------------------------------------

def run_ge_checkpoint(df: pd.DataFrame, schema: DatasetSchema) -> tuple[bool, str]:
    try:
        ge_df = ge.dataset.PandasDataset(df)
        failures = []

        for col in schema.columns:
            if col.name not in df.columns:
                continue  # already caught by compare_schema; skip defensively

            if not col.nullable:
                result = ge_df.expect_column_values_to_not_be_null(col.name)
                if not result["success"]:
                    unexpected = result["result"].get("unexpected_count", "?")
                    failures.append(f"'{col.name}' has {unexpected} null value(s), expected none")

            if col.allowed_values:
                result = ge_df.expect_column_values_to_be_in_set(col.name, col.allowed_values)
                if not result["success"]:
                    failures.append(f"'{col.name}' has values outside allowed set {col.allowed_values}")

            if col.min_value is not None or col.max_value is not None:
                result = ge_df.expect_column_values_to_be_between(
                    col.name, min_value=col.min_value, max_value=col.max_value
                )
                if not result["success"]:
                    failures.append(
                        f"'{col.name}' has values outside range "
                        f"[{col.min_value}, {col.max_value}]"
                    )

        for rule in schema.business_rules:
            if rule.rule_type == "positive" and rule.applies_to_column:
                kwargs = dict(column=rule.applies_to_column, min_value=0)
                if rule.condition_column:
                    kwargs["row_condition"] = (
                        f'{rule.condition_column} == "{rule.condition_equals}"'
                    )
                    kwargs["condition_parser"] = "pandas"
                result = ge_df.expect_column_values_to_be_between(**kwargs)
                if not result["success"]:
                    failures.append(f"business rule '{rule.name}' violated: {rule.description}")

        if failures:
            remarks = "; ".join(failures[:3])
            if len(failures) > 3:
                remarks += f" (+{len(failures) - 3} more)"
            return False, remarks
        return True, "All checks successful"

    except Exception as e:
        # A GE API surprise shouldn't crash the worker — treat it as a failed
        # checkpoint with the exception surfaced, so it's visible and fixable.
        return False, f"GE checkpoint raised an exception: {e}"


# ---------------------------------------------------------------------------
# Core handler — shared by both the MQTT callback and startup reconciliation
# ---------------------------------------------------------------------------

def process_execution(execution_id: str, dataset: str) -> None:
    run = load_runs_db.get_run(execution_id)
    if run is None:
        console.log_error(f"No load_runs entry for execution_id={execution_id} — skipping")
        return

    if run["ingestion_status"] != "SUCCESS":
        console.log_info(
            f"Skipping {execution_id}: ingestion_status={run['ingestion_status']} (not SUCCESS yet)"
        )
        return

    if run["dq_status"] is not None:
        console.log_info(f"Skipping {execution_id}: already evaluated (dq_status={run['dq_status']})")
        return

    try:
        schema = get_dataset_schema(dataset)
        file_path = run["file_path"]
        df = load_dataframe(file_path, schema.file_format)

        schema_ok, schema_remarks = compare_schema(df, schema)
        if not schema_ok:
            load_runs_db.set_dq_status(execution_id, "DQ_FAILED", schema_remarks)
            console.log_warning(f"DQ_FAILED (schema drift) — {execution_id} [{dataset}]\n    {schema_remarks}")
            publish_message(ANOMALY_ALERT, {"execution_id": execution_id})
            return

        ref_ok, ref_remarks = check_referential_integrity(df, schema)
        if not ref_ok:
            load_runs_db.set_dq_status(execution_id, "DQ_FAILED", ref_remarks)
            console.log_warning(f"DQ_FAILED (referential integrity) — {execution_id} [{dataset}]\n    {ref_remarks}")
            publish_message(ANOMALY_ALERT, {"execution_id": execution_id})
            return

        ge_passed, ge_remarks = run_ge_checkpoint(df, schema)
        if ge_passed:
            load_runs_db.set_dq_status(execution_id, "DQ_PASSED", ge_remarks)
            console.log_success(f"DQ_PASSED — {execution_id} [{dataset}]")
        else:
            load_runs_db.set_dq_status(execution_id, "DQ_FAILED", ge_remarks)
            console.log_warning(f"DQ_FAILED (GE checkpoint) — {execution_id} [{dataset}]\n    {ge_remarks}")
            publish_message(ANOMALY_ALERT, {"execution_id": execution_id})

    except Exception as e:
        # Any unexpected error (file missing, unreadable, etc.) still needs to
        # resolve dq_status — otherwise the row sits at NULL forever, looking
        # identical to "not yet processed" rather than "processing broke".
        remarks = f"DQ pipeline error: {e}"
        load_runs_db.set_dq_status(execution_id, "DQ_FAILED", remarks)
        console.log_error(f"DQ pipeline error on {execution_id}: {e}")
        publish_message(ANOMALY_ALERT, {"execution_id": execution_id})


def reconcile_pending() -> None:
    """
    On worker startup, catch up on anything ingested while this worker was
    down. MQTT's default QoS doesn't guarantee delivery to an absent
    subscriber, so this is the safety net, not an optional nicety.
    """
    pending = load_runs_db.get_pending_dq_runs()
    if not pending:
        console.log_info("No pending DQ runs to reconcile on startup.")
        return
    console.log_info(f"Reconciling {len(pending)} pending run(s) from before startup...")
    for run in pending:
        process_execution(run["execution_id"], run["dataset"])


# ---------------------------------------------------------------------------
# MQTT wiring
# ---------------------------------------------------------------------------

def on_connect(client, userdata, flags, reason_code, properties=None):
    console.log_success(f"Connected to MQTT broker (reason_code={reason_code})")
    client.subscribe(INGESTION_COMPLETE)
    console.log_info(f"Subscribed to '{INGESTION_COMPLETE}'")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        execution_id = payload["execution_id"]
        dataset = payload["dataset"]
        console.log_info(f"Received event: execution_id={execution_id}, dataset={dataset}")
        process_execution(execution_id, dataset)
    except Exception as e:
        console.log_error(f"Failed to process incoming message: {e}")


def main():
    load_runs_db.init_db()
    reconcile_pending()

    host = os.environ.get("MQTT_HOST", "localhost")
    port = int(os.environ.get("MQTT_PORT", 1883))

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    console.log_info(f"Connecting to MQTT broker at {host}:{port}...")
    client.connect(host, port)
    console.log_info("DQ worker running. Waiting for ingestion events (Ctrl+C to stop)...")
    client.loop_forever()


if __name__ == "__main__":
    main()