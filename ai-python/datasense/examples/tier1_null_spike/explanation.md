# Tier 1 — Null Spike

**What changed:** `last_name` is empty on `CUST-0003` and `CUST-0006` —
2 out of 8 rows (25%, matching `error_pct: 25` in the real scenario, scaled
down here to a small example).

**Why `last_name` specifically:** the real pipeline picks a RANDOM
non-nullable column from the Neo4j contract each time — it could just as
easily have hit `email` or `first_name`. `last_name` is used here purely as
one concrete illustration.

**Why this fails DQ, and how:**
1. `compare_schema()` passes — no columns added, removed, or renamed. The
   file structurally matches the contract.
2. The GE checkpoint runs `expect_column_values_to_not_be_null('last_name')`
   because the contract declares `last_name` with `nullable=False`. Two
   nulls exist where zero are allowed → expectation fails.
3. Result: `DQ_FAILED`, remark something like:
   `'last_name' has 2 null value(s), expected none`

**What this does NOT require:** no join, no lineage, no cross-dataset
reasoning. This is the simplest possible violation — a single column, in a
single file, checked against a single rule. This is intentionally the
"control group" tier — if an agent ever needed complex reasoning to catch
this, something would be over-engineered.
