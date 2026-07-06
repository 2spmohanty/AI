"""
storage/ground_truth_db.py

Schema + access functions for ground_truth.db — a PHYSICALLY SEPARATE SQLite
file from load_runs.db. This is deliberate isolation, not just a naming
convention: dq_pipeline.py and every future AI-layer tool should never import
this module or hold a connection to this file. It exists solely for
eval.py / LLM-as-judge to grade whether the agent's conclusions match what
was actually injected.

Append-only in practice — rows are written once at injection time and never
updated, unlike load_runs which mutates status as a run progresses.
"""

import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone

from datasense.storage.paths import GROUND_TRUTH_DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS injection_ground_truth (
    ground_truth_id             TEXT PRIMARY KEY,
    execution_id                TEXT NOT NULL,
    scenario_id                 TEXT,
    scenario_step               INTEGER,
    tier                        INTEGER NOT NULL,
    error_type                  TEXT NOT NULL,
    dataset                     TEXT NOT NULL,
    target_column               TEXT,
    requested_error_pct         REAL,
    actual_rows_affected        INTEGER,
    upstream_execution_id       TEXT,
    is_cascade_origin           INTEGER NOT NULL DEFAULT 0,
    resolves_ground_truth_id    TEXT,
    description                 TEXT,
    injected_at                 TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_ground_truth_execution_id
    ON injection_ground_truth (execution_id);

CREATE INDEX IF NOT EXISTS idx_ground_truth_scenario_id
    ON injection_ground_truth (scenario_id);
"""


@contextmanager
def get_connection():
    conn = sqlite3.connect(GROUND_TRUTH_DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        conn.executescript(SCHEMA)


def record_injection(
    execution_id: str,
    tier: int,
    error_type: str,
    dataset: str,
    target_column: str = None,
    requested_error_pct: float = None,
    actual_rows_affected: int = None,
    upstream_execution_id: str = None,
    is_cascade_origin: bool = False,
    resolves_ground_truth_id: str = None,
    description: str = "",
    scenario_id: str = None,
    scenario_step: int = None,
) -> str:
    """
    Called by the ingestion engine after EVERY run completes, including
    clean ones. Clean runs are recorded with tier=0, error_type="clean" —
    deliberately, not skipped — so eval.py can distinguish "no ground truth
    row exists" (a bug in the pipeline) from "this run was genuinely clean"
    (an expected, common outcome). Without this, a missing row is ambiguous.
    """
    ground_truth_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO injection_ground_truth (
                ground_truth_id, execution_id, scenario_id, scenario_step,
                tier, error_type, dataset, target_column,
                requested_error_pct, actual_rows_affected,
                upstream_execution_id, is_cascade_origin,
                resolves_ground_truth_id, description, injected_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ground_truth_id, execution_id, scenario_id, scenario_step,
                tier, error_type, dataset, target_column,
                requested_error_pct, actual_rows_affected,
                upstream_execution_id, int(is_cascade_origin),
                resolves_ground_truth_id, description, now,
            ),
        )
    return ground_truth_id


def get_ground_truth_by_execution_id(execution_id: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM injection_ground_truth WHERE execution_id = ?",
            (execution_id,),
        ).fetchone()
        return dict(row) if row else None


def get_scenario_chain(scenario_id: str) -> list[dict]:
    """Full ordered sequence of injections belonging to one cascade scenario."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM injection_ground_truth
            WHERE scenario_id = ?
            ORDER BY scenario_step ASC
            """,
            (scenario_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_cascade_origin(scenario_id: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT * FROM injection_ground_truth
            WHERE scenario_id = ? AND is_cascade_origin = 1
            LIMIT 1
            """,
            (scenario_id,),
        ).fetchone()
        return dict(row) if row else None