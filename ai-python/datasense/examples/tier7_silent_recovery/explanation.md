# Tier 7 — Silent Recovery

**The 2 files:**

1. `step1_customer_failed.csv` — 2 of 5 rows have a null `email`
   (`CUST-9002`, `CUST-9004`). Fires `DQ_FAILED`, exactly like the Tier 1
   example — nothing new here mechanically.
2. `step2_customer_recovered.csv` — a completely separate, later customer
   batch. Every row is clean. No intervention happened in between — this is
   just the next normal ingestion run, and whatever caused step 1's nulls
   (a bad upstream job, a config typo, anything) simply isn't present
   anymore.

**Why this needs its own ground-truth wiring, not just two independent
records:** in `ground_truth.db`, step 2's row has
`resolves_ground_truth_id` pointing at step 1's `ground_truth_id`. Without
that link, step 2 looks like just another unremarkable clean run —
indistinguishable from the thousands of other clean runs elsewhere in the
system. WITH the link, it's specifically flagged as "the run that resolved
a known prior failure," which is what `eval.py` will eventually use to
check whether an agent correctly notices "already fixed, don't escalate"
rather than treating step 1's old alert as still-open.

**The behavior this is testing isn't detection — it's restraint.** A
naive agent monitoring for `DQ_FAILED` alerts might see step 1's alert,
start investigating, and — if it re-checks the customer dataset later
without noticing time has passed — could keep escalating an issue that
resolved itself hours or days ago. Recognizing "this was already fixed" is
just as important as recognizing "this is broken" in a real operational
system, and it's easy to get catastrophically wrong by over-alerting on
stale information.
