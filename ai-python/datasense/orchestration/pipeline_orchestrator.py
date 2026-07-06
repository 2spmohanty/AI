"""
orchestration/pipeline_orchestrator.py

Runs a sequence of ingestion steps defined in a YAML scenario file, chaining
them into a single scenario_id so ground_truth.db can later reconstruct the
full intended cascade. Each step calls run_ingestion() directly (no
subprocess) via the same function the CLI uses.

Usage:
    uv run python -m datasense.orchestration.pipeline_orchestrator \\
        --scenario datasense/scenarios/customer_volume_cascade.yaml

Scenario YAML schema:

    scenario_name: customer_volume_cascade
    description: Optional free-text description
    steps:
      - step: 1                    # required, unique within the file
        dataset: customer
        rows: 500
        # error_type / error_pct / error_column / seed all optional, default clean
      - step: 2
        dataset: customer
        rows: 300
        error_type: volume_drop
        error_pct: 40
        is_cascade_origin: true     # marks this as the true root cause for eval
      - step: 3
        dataset: account
        rows: 500
        fk_source_step: 2          # <-- pin FK sampling to step 2's output,
                                    #     NOT a random DQ_PASSED partition.
                                    #     Without this, a scripted cascade can
                                    #     silently sample the wrong upstream
                                    #     batch if multiple DQ_PASSED partitions
                                    #     exist for the same dataset.
      - step: 4
        dataset: transaction
        rows: 800
        fk_source_step: 3
        wait_for_dq: false          # optional, default true — set false to
                                     # fire-and-move-on without blocking

Every step waits for DQ resolution by default before the next step runs,
since downstream FK sampling requires the upstream partition to already be
DQ_PASSED. Set wait_for_dq: false on a step only if you know the next step
doesn't depend on it.
"""

import argparse
import time
import uuid

import yaml

from datasense.ingestion.ingestion_engine import run_ingestion
from datasense.storage import load_runs_db, ground_truth_db
from datasense.common import console

DEFAULT_TIMEOUT_SECONDS = 60
POLL_INTERVAL_SECONDS = 1.5


def wait_for_dq_resolution(execution_id: str, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> str:
    """
    Polls load_runs.db until dq_status is set. Necessary because the DQ
    worker resolves asynchronously over MQTT — the orchestrator has no
    direct handle on when that finishes, only the shared table both sides
    read/write.
    """
    elapsed = 0
    while elapsed < timeout_seconds:
        run = load_runs_db.get_run(execution_id)
        if run and run["dq_status"] is not None:
            return run["dq_status"]
        time.sleep(POLL_INTERVAL_SECONDS)
        elapsed += POLL_INTERVAL_SECONDS
    return "TIMEOUT"


def load_scenario(scenario_path: str) -> dict:
    with open(scenario_path, "r") as f:
        scenario = yaml.safe_load(f)

    steps = scenario.get("steps", [])
    if not steps:
        raise ValueError("Scenario file has no steps defined")

    step_numbers = [s["step"] for s in steps]
    if len(step_numbers) != len(set(step_numbers)):
        raise ValueError(f"Duplicate 'step' numbers in scenario: {step_numbers}")

    return scenario


def run_scenario(scenario_path: str) -> str:
    scenario = load_scenario(scenario_path)
    scenario_id = str(uuid.uuid4())
    scenario_name = scenario.get("scenario_name", "unnamed_scenario")

    console.console.rule(f"[bold]Scenario: {scenario_name}[/bold] (scenario_id={scenario_id})")
    if scenario.get("description"):
        console.log_info(scenario["description"])

    step_execution_ids: dict[int, str] = {}

    for step_def in scenario["steps"]:
        step_num = step_def["step"]
        dataset = step_def["dataset"]

        fk_source_step = step_def.get("fk_source_step")
        if fk_source_step is not None:
            if fk_source_step not in step_execution_ids:
                raise ValueError(
                    f"Step {step_num} references fk_source_step={fk_source_step}, "
                    f"which hasn't run yet or doesn't exist"
                )
            source_execution_id = step_execution_ids[fk_source_step]
        else:
            source_execution_id = step_def.get("source_execution_id")

        resolves_step = step_def.get("resolves_step")
        resolves_ground_truth_id = None
        if resolves_step is not None:
            if resolves_step not in step_execution_ids:
                raise ValueError(
                    f"Step {step_num} references resolves_step={resolves_step}, "
                    f"which hasn't run yet or doesn't exist"
                )
            prior_ground_truth = ground_truth_db.get_ground_truth_by_execution_id(
                step_execution_ids[resolves_step]
            )
            if prior_ground_truth is None:
                raise ValueError(f"No ground truth record found for step {resolves_step}")
            resolves_ground_truth_id = prior_ground_truth["ground_truth_id"]

        console.console.rule(f"Step {step_num}: {dataset}", style="dim")

        execution_id = run_ingestion(
            dataset=dataset,
            rows=step_def.get("rows", 100),
            error_pct=step_def.get("error_pct", 0.0),
            error_type=step_def.get("error_type"),
            error_column=step_def.get("error_column"),
            seed=step_def.get("seed"),
            source_execution_id=source_execution_id,
            is_cascade_origin=step_def.get("is_cascade_origin", False),
            resolves_ground_truth_id=resolves_ground_truth_id,
            scenario_id=scenario_id,
            scenario_step=step_num,
        )
        step_execution_ids[step_num] = execution_id

        wait_for_dq = step_def.get("wait_for_dq", True)
        if wait_for_dq:
            console.log_info(f"Waiting for DQ resolution on {execution_id}...")
            dq_status = wait_for_dq_resolution(execution_id)
            if dq_status == "DQ_PASSED":
                console.log_success(f"Step {step_num} resolved: DQ_PASSED")
            elif dq_status == "DQ_FAILED":
                run = load_runs_db.get_run(execution_id)
                console.log_warning(f"Step {step_num} resolved: DQ_FAILED — {run['dq_remarks']}")
            else:
                console.log_error(
                    f"Step {step_num} timed out waiting for DQ resolution — "
                    f"is the DQ worker (dq_pipeline.py) running?"
                )

    print_scenario_summary(scenario_id, scenario_name)
    return scenario_id


def print_scenario_summary(scenario_id: str, scenario_name: str) -> None:
    console.console.rule(f"[bold]Scenario Summary: {scenario_name}[/bold]")
    chain = ground_truth_db.get_scenario_chain(scenario_id)
    for entry in chain:
        run = load_runs_db.get_run(entry["execution_id"])
        origin_marker = " [CASCADE ORIGIN]" if entry["is_cascade_origin"] else ""
        console.console.print(
            f"  step {entry['scenario_step']}: {entry['dataset']} — "
            f"tier {entry['tier']} ({entry['error_type']}) — "
            f"dq_status={run['dq_status']}{origin_marker}"
        )
    console.log_info(f"Full scenario_id for reference: {scenario_id}")


def main():
    parser = argparse.ArgumentParser(description="DataSense scenario orchestrator")
    parser.add_argument("--scenario", required=True, help="Path to scenario YAML file")
    args = parser.parse_args()
    run_scenario(args.scenario)


if __name__ == "__main__":
    main()