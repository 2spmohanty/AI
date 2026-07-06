# Tier 4 — Temporal Cascade (Account-Origin)

**Same mechanism as the customer-origin cascade, one layer further down.**

1. `step1_customer_healthy.csv` — 5 customers, completely normal. The root
   cause is deliberately NOT here this time.
2. `step2_account_shrunk.csv` — 5 accounts, all with perfectly valid
   `customer_id` references back to step 1. In the real pipeline this would
   be requested at a higher row count (e.g. 8) with `error_pct: 40`
   (volume_drop), silently landing fewer accounts than intended. Every
   account that exists is completely legitimate.
3. `step3_transaction_downstream.json` — 4 transactions, all referencing
   accounts from step 2's shrunk batch.

**Why this variant exists separately from the customer-origin cascade:** if
the only cascade example ever shown always has Customer as the root cause,
an AI investigation could learn a shortcut — "when in doubt, blame Customer"
— without actually reasoning about lineage. This version proves the pattern
generalizes: the root cause can sit at ANY layer, and the correct approach
is always the same — compare row counts across time for each dataset
independently, don't assume based on position in the hierarchy.

**What passes, and why:** all three files are completely clean by every
deterministic check available. Referential integrity holds throughout,
no nulls, no schema drift, no business rule violations. The account batch
is just smaller than it should be — and only a historical baseline
comparison at the ACCOUNT layer specifically would reveal that.
