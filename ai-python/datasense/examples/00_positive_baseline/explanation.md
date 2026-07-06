# Positive Baseline

Three files, fully consistent with each other and with the Neo4j contracts.

**customer.csv** — 5 customers. Notice `CUST-0005` has an empty
`customer_segment` — that's fine, the contract declares that column
`nullable=True`. This is normal optionality, not an anomaly.

**account.csv** — 6 accounts. Every `customer_id` (e.g. `CUST-0001`,
`CUST-0002`...) exists in `customer.csv`. Note `CUST-0001` appears twice
(`ACC-1001` and `ACC-1006`) — one customer can hold multiple accounts, which
is exactly what the `child_of` relationship in Neo4j models.

**transaction.json** — 5 transactions. Every `account_id` exists in
`account.csv`. Look at the `amount` field by `transaction_type`:
- `DEPOSIT` → always positive (500.00, 75.20) — this is the business rule
  `deposit_amount_positive` from the contract.
- `WITHDRAWAL` / `FEE` → negative, realistic.
- `TRANSFER` → can go either way (shown here as positive, an inbound transfer).

**Why this passes DQ:** schema matches the contract exactly (right columns,
right types), no nulls where they're not allowed, every FK resolves to a
real parent row, every business rule holds. There's nothing for any check
to flag.
