# Tier 3 — Schema Type Change

**What changed:** look very closely at `amount` in both files. Before:
`"amount": 500.00` — a bare JSON number. After: `"amount": "500.0"` — the
exact same value, but wrapped in quotes, making it a JSON string. Visually
almost identical; structurally a completely different data type.

**Why this is subtle and easy to miss by eye, but not by machine:** JSON
(unlike CSV) actually distinguishes `500.0` from `"500.0"` at the type
level. When `dq_pipeline.py` loads this file, it deliberately does NOT use
`pd.read_json()` — that function tries to be "helpful" and auto-converts
numeric-looking strings back into floats, which would silently erase this
exact anomaly before any check even saw it. Instead it uses `json.load()` +
`pd.DataFrame(records)`, which preserves the true type: a column that's now
entirely strings becomes `dtype=object`, not `float64`.

**Note for CSV datasets (Customer, Account):** this same anomaly type
behaves differently there, because CSV has no native type distinction — a
number written as text reads back as a number regardless of quotes. So for
CSV files, the injector instead appends a non-numeric suffix (e.g.
`4200.50_CORRUPT`) to force a genuine, unparseable string — otherwise the
anomaly would be silently defeated the same way `pd.read_json()` would
defeat it here.

**How it's caught:** `compare_schema()` infers the actual category of each
column (`numeric` vs `string`) from the loaded DataFrame's dtype and
compares it against the contract's declared type (`amount` → `FLOAT` →
expected `numeric`). Here, the actual dtype is `object` (string) —
mismatch.

**Result:** `DQ_FAILED`, remark: `Schema drift: 'amount' expected numeric
(FLOAT), found string (str)`
