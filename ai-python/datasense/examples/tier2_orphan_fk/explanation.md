# Tier 2 — Orphan Foreign Key

**What changed:** `ACC-1002` and `ACC-1007` had valid `customer_id` values
(`CUST-0002` twice). Both were replaced with fabricated IDs
(`ORPHAN-7F3A9C2E`, `ORPHAN-B81DE045`) that don't exist anywhere in
`customer.csv`.

**Why GE alone can't catch this:** look at the `account_after.csv` file in
isolation — every column is present, every type is right, `customer_id` is
non-null on every row, nothing looks structurally wrong. GE's checks are all
*single-column* constraints (non-null, range, categorical). None of them
ask "does this value exist somewhere else, in a different file entirely?"
That's a join, not a column check — a fundamentally different kind of
question.

**How it's actually caught:** `check_referential_integrity()` in
`dq_pipeline.py` builds the full set of valid `customer_id` values by
reading every `DQ_PASSED` customer partition (not just this run's specific
upstream file — ALL of them), then checks every `account_id`'s
`customer_id` against that set. `ORPHAN-7F3A9C2E` and `ORPHAN-B81DE045`
aren't in it.

**Result:** `DQ_FAILED`, remark: `'customer_id' has 2/7 row(s) referencing
non-existent customer.customer_id (orphaned, no matching parent)`

**Why this is Tier 2, not Tier 1:** this is the first case that genuinely
requires looking at TWO datasets together, not one. It's still simple —
a single join, no time dimension, no ambiguity about which parent record is
"correct" — but it's a qualitatively different kind of check than anything
in Tier 1.
