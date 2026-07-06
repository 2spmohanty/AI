# DataSense — Illustrated Examples

Small, hand-written examples (5-8 rows each) showing exactly what each
scenario does to the data and why DQ reacts the way it does. These are NOT
what the pipeline actually generates (that's Faker-driven, hundreds of rows,
random column targeting) — they're simplified stand-ins so the mechanics are
visible at a glance.

Each folder has a `before.*` / `after.*` pair (or just `after.*` where there's
no meaningful "before") and an `explanation.md` walking through what changed
and why.

| Folder | Maps to real scenario | DQ result |
|---|---|---|
| `00_positive_baseline/` | `positive_baseline_chain.yaml` | all DQ_PASSED |
| `tier1_null_spike/` | `tier1_null_spike.yaml` | DQ_FAILED |
| `tier1_negative_amount/` | `tier1_negative_amount.yaml` | DQ_FAILED |
| `tier2_orphan_fk/` | `tier2_orphan_fk.yaml` | DQ_FAILED |
| `tier3_schema_rename/` | `tier3_schema_rename.yaml` | DQ_FAILED |
| `tier3_schema_type_change/` | `tier3_schema_type_change.yaml` | DQ_FAILED |
| `tier4_customer_volume_cascade/` | `customer_volume_cascade.yaml` | all DQ_PASSED (invisible) |
| `tier4_account_volume_cascade/` | `tier4_account_volume_cascade.yaml` | all DQ_PASSED (invisible) |
| `tier5_statistical_drift/` | `tier5_statistical_drift.yaml` | DQ_PASSED (invisible) |
| `tier6_composite/` | `tier6_composite.yaml` | 2 unrelated DQ_FAILED |
| `tier7_silent_recovery/` | `tier7_silent_recovery.yaml` | fail then recover |

Read these in order — each builds on the contract/column names introduced in
`00_positive_baseline/`.

---

## Where AI Triage Is Actually Needed — and Where It's Overkill

A recurring temptation on projects like this is to point an LLM at every
alert "just in case." That's not free — it's slower, costs money per
investigation, and worse, it trains you to trust a black box for things a
five-line rule already handles correctly. The honest breakdown, tier by
tier:

| Tier | Detection | Root cause / explanation | Verdict |
|---|---|---|---|
| 1 — null_spike, negative_amount | Single-column rule | The remark string IS the root cause | **DQ sufficient. AI is overkill.** |
| 2 — orphan_fk | Single join | The remark string IS the root cause | **DQ sufficient. AI is overkill.** |
| 3 — schema_rename, schema_type_change | Structural diff against Neo4j | Usually self-evident from the diff itself | **DQ sufficient for detection.** AI *could* add a "this looks like a rename of X→Y" suggestion, but that's a convenience, not a necessity. |
| 4 — temporal cascade | Needs a row-count baseline check (see note below) | Needs multi-hop lineage walk + hypothesis ranking | **AI genuinely required** for the causal explanation — detection alone can be a simple statistical rule (see below). |
| 5 — statistical drift | Could be a z-score / control-chart rule | Needs context (business event? bug? fraud?) to be useful | **Borderline.** Detection can be deterministic; *explaining* it well benefits from AI. |
| 6 — composite/confounded | Each failure alone is trivial (Tier 1/2 level) | Needs to actively rule out false correlation | **AI genuinely required** — not for detecting either failure, but for NOT wrongly linking them. |
| 7 — silent recovery | "Prior alert + now passing" is a simple state check | Needs judgment on WHY it recovered and whether to trust it | **Borderline.** The bookkeeping is deterministic; deciding whether a self-healed issue is safely closed or a warning sign benefits from AI. |

### Why Tiers 1–3 don't need AI at all

For these, the DQ remark already names the exact column, the exact rule,
and the exact count of affected rows. There is no ambiguity left to
resolve and no hypothesis to weigh — routing this through an LLM adds
latency and cost to re-derive a conclusion the deterministic layer already
stated correctly. The only legitimate AI use here would be cosmetic: turning
`'last_name' has 60 null value(s), expected none` into a friendlier
sentence for a non-technical stakeholder. That's a UX nicety, not
"agentic capability."

### The important nuance on Tier 4 and Tier 5: detection vs. explanation are separable

It's tempting to say "volume anomalies and statistical drift need AI" as a
blanket statement — but *noticing* a row-count drop or a value spike is
actually still automatable with a plain statistical rule (e.g. "alert if
today's row count is >30% below the trailing 7-run average"). That's just
another deterministic check, no different in kind from what
`dq_pipeline.py` already does — it's simply comparing against history
instead of a fixed threshold. Adding it wouldn't require AI at all.

What genuinely can't be reduced to a rule is the *explanation* once
something's flagged: **which specific downstream batches were built from
the anomalous data, going back through Neo4j's lineage, and which of
several plausible stories best fits the evidence.** That's combinatorial
and context-dependent in a way that doesn't compress into an `if` statement
— it's the actual reasoning task, not the trigger.

### Why Tier 6 and Tier 7 are where an agent earns its keep

Tier 6 isn't hard because either failure is hard to detect — both are
trivial, already-solved Tier 1/2 problems. It's hard because the natural
human (and naive-agent) instinct is to link two things that happened close
together in time, and actively resisting that requires checking lineage
to confirm or rule out a connection — a genuine reasoning step, not a
lookup.

Tier 7 is subtle in a different way: recognizing "this was already fixed"
requires comparing against the specific prior incident, not just checking
"is today's data clean" — and deciding whether a self-resolved issue is
truly closed or a symptom of something flaky and recurring is a judgment
call, not a lookup, even though the underlying state check
(`resolves_ground_truth_id` exists and points to a stale alert) is
completely mechanical.