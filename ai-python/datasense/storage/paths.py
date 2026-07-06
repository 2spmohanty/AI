"""
storage/paths.py

Single source of truth for where the .db files live. Resolved relative to
this file's location (datasense/storage/), not the caller's cwd — so
`uv run python -m datasense.metadata.load_contracts` and a pytest run from
some other directory both land on the same physical files.
"""

from pathlib import Path

DATASENSE_ROOT = Path(__file__).resolve().parent.parent  # .../datasense/
DATA_DIR = DATASENSE_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

INBOUND_DIR = DATASENSE_ROOT / "inbound"
INBOUND_DIR.mkdir(parents=True, exist_ok=True)

LOAD_RUNS_DB_PATH = DATA_DIR / "load_runs.db"
GROUND_TRUTH_DB_PATH = DATA_DIR / "ground_truth.db"