"""
storage/load_runs_db.py

Schema + access functions for load_runs.db — the operational audit trail.
This is the ONE table the DQ pipeline updates and the AI layer is allowed
to read. It contains only what actually, mechanically happened: which file,
which dataset, what status, what symptom. No "why" — never a root-cause
judgment. That lives exclusively in ground_truth.db (see ground_truth_db.py).

Two INDEPENDENT status axes, deliberately not collapsed into one column:

  ingestion_status : INITIATED -> RUNNING -> SUCCESS | FAILED
      Mechanical: did the generator produce a file and write it to disk.
      Has nothing to do with data quality.

  dq_status        : NULL (not yet evaluated) -> DQ_PASSED | DQ_FAILED
      Only meaningful once ingestion_status = SUCCESS. Set exclusively by
      dq_pipeline.py. A row sitting at ingestion_status=SUCCESS with
      dq_status=NULL means "DQ hasn't picked it up yet" — a legitimate,
      queryable in-between state, not a bug.

Why split: a row stuck at ingestion_status=RUNNING is diagnosable as a
crashed ingestion process. A row at ingestion_status=SUCCESS with
dq_status=NULL for a suspiciously long time is diagnosable as a stalled or
dead DQ worker. Collapsing both into one field loses that distinction.
"""

import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone

from datasense.storage.paths import LOAD_RUNS_DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS load_runs (
    execution_id        TEXT PRIMARY KEY,
    dataset              TEXT NOT NULL,
    partition_date        TEXT NOT NULL,
    file_path             TEXT NOT NULL,
    row_count             INTEGER,
    ingestion_status      TEXT NOT NULL DEFAULT 'INITIATED',
    ingestion_remarks     TEXT,
    dq_status             TEXT,
    dq_remarks            TEXT,
    created_at            TEXT NOT NULL,
    updated_at            TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_load_runs_dataset_dq_status
    ON load_runs (dataset, dq_status);

CREATE INDEX IF NOT EXISTS idx_load_runs_dataset_ingestion_status
    ON load_runs (dataset, ingestion_status);

CREATE INDEX IF NOT EXISTS idx_load_runs_created_at
    ON load_runs (created_at);
"""

VALID_INGESTION_STATUSES = {"INITIATED", "RUNNING", "SUCCESS", "FAILED"}
VALID_DQ_STATUSES = {"DQ_PASSED", "DQ_FAILED"}


@contextmanager
def get_connection():
    conn = sqlite3.connect(LOAD_RUNS_DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        conn.executescript(SCHEMA)


def start_run(dataset: str, partition_date: str, file_path: str) -> str:
    """
    Inserts a new row at ingestion_status=INITIATED, dq_status=NULL.
    Returns the generated execution_id. Called by ingestion_engine.py
    BEFORE data generation begins — not after the file is written — so the
    row exists and is queryable for the whole duration of a run, including
    if it crashes mid-generation.
    """
    execution_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO load_runs
                (execution_id, dataset, partition_date, file_path, row_count,
                 ingestion_status, ingestion_remarks, dq_status, dq_remarks,
                 created_at, updated_at)
            VALUES (?, ?, ?, ?, NULL, 'INITIATED', NULL, NULL, NULL, ?, ?)
            """,
            (execution_id, dataset, partition_date, file_path, now, now),
        )
    return execution_id


def mark_running(execution_id: str) -> None:
    _set_ingestion_status(execution_id, "RUNNING")


def mark_ingestion_success(execution_id: str, row_count: int,
                            remarks: str = None) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE load_runs
            SET ingestion_status = 'SUCCESS', row_count = ?,
                ingestion_remarks = ?, updated_at = ?
            WHERE execution_id = ?
            """,
            (row_count, remarks, now, execution_id),
        )


def mark_ingestion_failed(execution_id: str, remarks: str) -> None:
    _set_ingestion_status(execution_id, "FAILED", remarks)


def _set_ingestion_status(execution_id: str, status: str, remarks: str = None) -> None:
    if status not in VALID_INGESTION_STATUSES:
        raise ValueError(f"Invalid ingestion_status: {status}")
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE load_runs
            SET ingestion_status = ?, ingestion_remarks = COALESCE(?, ingestion_remarks),
                updated_at = ?
            WHERE execution_id = ?
            """,
            (status, remarks, now, execution_id),
        )


def set_dq_status(execution_id: str, dq_status: str, remarks: str = None) -> None:
    """
    Called exclusively by dq_pipeline.py once schema/GE validation completes.
    Never touches ingestion_status — the two axes are updated independently.
    """
    if dq_status not in VALID_DQ_STATUSES:
        raise ValueError(f"Invalid dq_status: {dq_status}")
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE load_runs
            SET dq_status = ?, dq_remarks = ?, updated_at = ?
            WHERE execution_id = ?
            """,
            (dq_status, remarks, now, execution_id),
        )


def get_run(execution_id: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM load_runs WHERE execution_id = ?", (execution_id,)
        ).fetchone()
        return dict(row) if row else None


def get_run_by_id_or_raise(execution_id: str) -> dict:
    """Used when an explicit --source-execution-id override is passed for determinism."""
    run = get_run(execution_id)
    if run is None:
        raise ValueError(f"No load_runs entry found for execution_id={execution_id}")
    return run


def get_random_dq_passed_partition(dataset: str) -> dict | None:
    """
    Used by generator.py for FK sampling in positive scenarios. Picks a
    RANDOM partition with dq_status=DQ_PASSED (implies ingestion_status=SUCCESS
    already, but both are checked explicitly for safety) — not the latest,
    per project design decision.
    """
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT * FROM load_runs
            WHERE dataset = ? AND ingestion_status = 'SUCCESS' AND dq_status = 'DQ_PASSED'
            ORDER BY RANDOM() LIMIT 1
            """,
            (dataset,),
        ).fetchone()
        return dict(row) if row else None


def get_recent_runs(dataset: str, limit: int = 20) -> list[dict]:
    """
    Used for statistical baseline comparisons (Tier 5 drift detection) — pull
    recent DQ_PASSED runs for a dataset to compute historical row_count trends.
    """
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM load_runs
            WHERE dataset = ? AND ingestion_status = 'SUCCESS' AND dq_status = 'DQ_PASSED'
            ORDER BY created_at DESC LIMIT ?
            """,
            (dataset, limit),
        ).fetchall()
        return [dict(r) for r in rows]


def get_all_dq_passed_runs(dataset: str) -> list[dict]:
    """
    ALL DQ_PASSED partitions for a dataset, not just recent ones. Used by
    dq_pipeline.py to build the full set of valid parent IDs for referential
    integrity checking — a FK value is only genuinely orphaned if it doesn't
    exist in ANY known-good parent partition, not just the most recent one.
    """
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM load_runs
            WHERE dataset = ? AND ingestion_status = 'SUCCESS' AND dq_status = 'DQ_PASSED'
            ORDER BY created_at ASC
            """,
            (dataset,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_pending_dq_runs(dataset: str = None) -> list[dict]:
    """
    Runs that finished ingesting successfully but haven't been DQ-evaluated
    yet. Useful for the DQ worker's own startup reconciliation (catch up on
    anything it missed while it was down) and for debugging a stalled worker.
    """
    with get_connection() as conn:
        if dataset:
            rows = conn.execute(
                """
                SELECT * FROM load_runs
                WHERE ingestion_status = 'SUCCESS' AND dq_status IS NULL
                AND dataset = ?
                ORDER BY created_at ASC
                """,
                (dataset,),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT * FROM load_runs
                WHERE ingestion_status = 'SUCCESS' AND dq_status IS NULL
                ORDER BY created_at ASC
                """
            ).fetchall()
        return [dict(r) for r in rows]