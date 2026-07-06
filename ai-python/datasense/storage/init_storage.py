"""
storage/init_storage.py

Creates both database files with their schemas. Idempotent — CREATE TABLE
IF NOT EXISTS means running this repeatedly is always safe.

Usage:
    uv run python -m datasense.storage.init_storage
"""

from datasense.storage import load_runs_db, ground_truth_db
from datasense.storage.paths import LOAD_RUNS_DB_PATH, GROUND_TRUTH_DB_PATH


def main():
    load_runs_db.init_db()
    print(f"load_runs.db ready at: {LOAD_RUNS_DB_PATH}")

    ground_truth_db.init_db()
    print(f"ground_truth.db ready at: {GROUND_TRUTH_DB_PATH}")

    print("\nBoth databases initialized. Confirming they are two separate files:")
    print(f"  load_runs.db     == ground_truth.db ? "
          f"{LOAD_RUNS_DB_PATH == GROUND_TRUTH_DB_PATH}")


if __name__ == "__main__":
    main()