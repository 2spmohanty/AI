# Tier 4 — Temporal Cascade (Customer-Origin)

**The 4 files, read in order:**

1. `step1_customer_healthy.csv` — 8 customers. A normal, healthy batch.
   Ignore this one going forward — it's shown only as a size reference for
   "what normal looks like."
2. `step2_customer_shrunk.csv` — a DIFFERENT, separate customer batch.
   Only 5 customers. In the real pipeline this would be requested at, say,
   8 rows with `error_pct: 40` (volume_drop), so ~3 rows get silently
   dropped, leaving 5. Every row that survives is completely valid — real
   names, real emails, nothing broken.
3. `step3_account_downstream.csv` — 6 accounts. Every single `customer_id`
   here (`CUST-1001` through `CUST-1005`) comes from **step 2's shrunk
   batch**, not step 1's healthy one. This is the `fk_source_step`
   mechanism forcing FK sampling to a specific upstream partition — in
   reality it's random, which is exactly why scripted scenarios need to pin
   it deliberately.
4. `step4_transaction_downstream.json` — 5 transactions, all referencing
   accounts from step 3.

**Why every single file passes DQ on its own:**
- Step 2: no null, no bad type, no broken rule. Just fewer rows than
  "normal" — and "normal" isn't a concept any single-file check has access
  to.
- Step 3: every `customer_id` resolves to a real row in step 2. Perfect
  referential integrity — just against a smaller-than-usual parent set.
- Step 4: same story, one layer further down.

**The actual problem, visible only by looking ACROSS files and time:**
step 2 has 5 customers where a healthy batch (step 1) had 8 — a ~40% drop.
Nobody downstream would ever know this by looking at their own file. The
only way to notice is to ask "is this customer batch smaller than the ones
before it?", and then trace forward through Neo4j's lineage
(`account CHILD_OF customer`, `transaction CHILD_OF account`) to confirm
that steps 3 and 4 were specifically built from the shrunken batch, not a
healthy one.

**This is exactly the reasoning gap deterministic DQ cannot close** — and
exactly what the AI investigation layer exists to do.
