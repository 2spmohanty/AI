# Tier 1 — Negative Amount (Business Rule Violation)

**What changed:** `TXN-9001` and `TXN-9003` were `DEPOSIT` transactions with
positive amounts (500.00, 1200.00). Both are now negative (-500.00,
-1200.00). Every other row is untouched — including the OTHER two DEPOSIT
rows (`TXN-9005`, `TXN-9006`), which stay positive. In the real pipeline
this is a random sample of eligible rows, not "every DEPOSIT."

**Why this is different from a simple range check:** the contract doesn't
say "amount must always be positive" — `WITHDRAWAL` and `FEE` are *supposed*
to be negative. The actual rule, from Neo4j, is conditional:

> `deposit_amount_positive`: amount must be positive **when
> transaction_type = DEPOSIT**

**How DQ catches it:** the GE checkpoint applies
`expect_column_values_to_be_between(column='amount', min_value=0,
row_condition='transaction_type == "DEPOSIT"')` — a row-conditional
expectation. It only evaluates the 4 DEPOSIT rows, and 2 of those 4 are
negative → fails.

**Result:** `DQ_FAILED`, remark: `business rule 'deposit_amount_positive'
violated: amount must be positive when transaction_type = DEPOSIT`

**Why this matters for later:** this is the first example where the check
isn't "does this column look right" but "does this column look right,
*given* what another column in the same row says." That conditional logic
is a small taste of the relational reasoning the AI layer will need much
more of.
