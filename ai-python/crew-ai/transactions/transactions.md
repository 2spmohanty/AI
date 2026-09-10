# TRANSACTION 1


### Anomaly type: Duplicate transaction and unusually large transaction.


- The transaction dated 2026-02-15 for Local Grocery Store, amount 124.50, appears twice (identical merchant, date, amount, and category).

- The transaction dated 2026-03-22 for Electronics Warehouse, amount 2,450.00, is substantially higher than the customer's normal spending pattern (typical transactions range from $4.65 to $229.92).

# TRANSACTION 2

### Anomaly type: Unusually small transaction and unexpected category.


- The transaction dated 2026-02-10 for Whole Foods Market, amount 0.50, is significantly lower than comparable grocery transactions (typical grocery spending ranges from $35.61 to $187.11).

- The transaction dated 2026-03-05 for Shell Gas Station, amount 45.00, is categorized under Dining instead of Transportation, representing a miscategorization anomaly.

# TRANSACTION 3

### Anomaly type: Recurring payment change and transaction spike.


- The Netflix subscription shows a recurring payment change: charged $15.99 on 2026-01-15 and 2026-02-15, but unexpectedly increases to $24.99 on 2026-03-15 (a 56% increase from the normal amount).

- A transaction spike occurs on 2026-03-20 with 5 transactions in a single day (Starbucks x3, Amazon, Target), which is unusually high compared to the typical 0-2 transactions per day in the rest of the dataset.

# TRANSACTION 4

### Anomaly type: Unusual merchant and weekend/unusual-time activity.


- The transaction dated 2026-02-28 for Luxury Jewelry Store, amount 3,500.00, represents an unusual merchant that does not fit the customer's normal spending pattern (all other merchants are everyday retailers and service providers).

- The transaction dated 2026-03-14 for High-End Restaurant, amount 450.00, occurs on a Saturday (weekend), while all other transactions in the dataset fall on weekdays (Monday–Friday), indicating unusual weekend activity for this customer.


# TRANSACTION 5

### Anomaly type: Frequency anomaly and refund anomaly.

- Local Cafe appears 6 times in March 2026 (dates: 2026-03-01, 2026-03-05, 2026-03-10, 2026-03-15, 2026-03-20, 2026-03-25), whereas this merchant typically appears only once per month in the customer's history, representing a frequency anomaly.

- A refund anomaly exists for Best Buy: a purchase of $89.99 on 2026-02-10 is followed by a refund of -$189.99 on 2026-02-15, which is $100 larger than the original purchase amount.


# TRANSACTION 6

### Anomaly type: None (clean dataset).


- This document contains 50 transactions with no deliberate anomalies.

- All transactions fall within expected ranges for their respective categories (Groceries: $25–200, Dining: $5–80, Utilities: $50–250, Fees: $2.50–35, Transportation: $10–100).

- Merchants are appropriately categorized, dates are valid and spread across January–March 2026, and there are no duplicates, outliers, miscategorizations, or unusual patterns.

This dataset can serve as a baseline or control for testing anomaly detection systems.