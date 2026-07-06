# Tier 6 — Composite / Confounded Anomaly

**The 3 files:**

1. `customer_shared_baseline.csv` — 4 healthy customers. Both failures
   below trace back to THIS same file — not to each other.
2. `customer_null_spike.csv` — a SEPARATE, later customer batch. 2 of 5
   rows have a null `email` (`CUST-6002`, `CUST-6004`). This alone is a
   plain Tier 1 failure, fires its own `DQ_FAILED` alert.
3. `account_orphan_fk.csv` — accounts sampled from the SHARED BASELINE
   (file 1), not from file 2. 2 of 4 rows have fabricated `customer_id`
   values. This alone is a plain Tier 2 failure, fires its own separate
   `DQ_FAILED` alert.

**The actual test here isn't detection — both failures are individually
trivial, already covered by Tier 1 and Tier 2.** The test is: **if these two
alerts land close together in time, does an investigation wrongly assume
they're related?**

They aren't. Notice `account_orphan_fk.csv` samples its (real) customer_id
values from `customer_shared_baseline.csv`, NOT from
`customer_null_spike.csv`. The two problems have completely independent
causes — one's a null in a later customer batch, the other is a broken FK
in an account batch built from an earlier, unrelated, perfectly healthy
customer batch. They just happen to have been ingested around the same
time.

**Why this matters:** a naive investigation might see "two DQ_FAILED alerts
close together, one on customer, one on account" and jump to "the account
failure must be caused by the customer failure" — a very human, very
tempting mistake, and exactly the kind of false-correlation an agent needs
to actively rule out (by checking lineage — does account_orphan_fk.csv
actually reference customer_null_spike.csv? No) rather than just
pattern-matching on timing.
