# Tier 5 — Statistical Drift (Semantic Shift)

**What changed:** `TXN-5002` (410.50 → 3284.00, an 8x multiplier) and
`TXN-5004` (275.00 → 2200.00, also 8x). Every other transaction is
untouched. In the real pipeline this is a random sample of rows on a random
numeric column, multiplied by a random factor between 5x-10x.

**Why NOTHING in the deterministic layer catches this — by design:**
- `amount` has no `min_value`/`max_value` range constraint in the contract
  broad enough to rule out 3284.00 as invalid — it's a perfectly plausible
  deposit amount on its own.
- The `deposit_amount_positive` business rule only checks the SIGN, not the
  magnitude. 3284.00 is positive → rule satisfied.
- There's no schema drift, no orphan FK, no null. Every column, every type,
  every relationship is exactly right.

**This passes `DQ_PASSED` — and that's the correct, intended outcome.**
The only way to know these two values are anomalous is to know what
"normal" looks like for this account, or this transaction type, over time —
i.e., a historical baseline. 410.50 and 275.00 are typical; 3284.00 and
2200.00 are 8x that. But "8x higher than usual" is a comparison against
history, not a fact you can check from this file alone.

**Why this is the clearest example of the project's core thesis:** this
tier exists specifically to demonstrate the boundary between what
deterministic rules can and cannot catch. Catching this requires comparing
against a historical baseline (the planned ChromaDB layer) — genuinely
AI-layer territory, not a gap in the DQ pipeline's implementation.
