# Tier 3 — Schema Rename (Unannounced Schema Drift)

**What changed:** the header. `customer_id` became `customer_identifier`.
Every value underneath is untouched — `CUST-0001` is still `CUST-0001`, just
sitting under a different column name. This simulates an upstream team
renaming a field without telling anyone downstream — a very real, very
common production incident.

**Why this is caught BEFORE any value-level check even runs:**
`compare_schema()` in `dq_pipeline.py` runs first, comparing the actual
column set in the file against the Neo4j contract's declared columns:

- Expected: `customer_id` — not found in the file → **missing column**
- Found in file: `customer_identifier` — not in the contract → **unexpected
  column**

Since the file structurally doesn't match the contract, the GE checkpoint
never runs at all — there's no point checking "is `customer_id` non-null"
against a file that doesn't even have a column by that name. Checking value
constraints on a structurally wrong file would be meaningless.

**Result:** `DQ_FAILED`, remark: `Schema drift: missing columns
['customer_id'], unexpected columns ['customer_identifier']`

**Why this is Tier 3, not Tier 1 or 2:** this isn't a bad VALUE — every
value here is perfectly valid. It's the STRUCTURE that changed. That's a
qualitatively different failure mode: nothing about looking at any single
row would tell you something's wrong. You have to know what columns are
*supposed* to exist to notice one is missing.
