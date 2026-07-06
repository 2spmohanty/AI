# SkillForge — AI Self-Assessment and Learning Path Generator

> **LangGraph Concepts Consolidation Project** | Python · LangGraph · Ollama · Local-first · Zero Cost

---

## What This Is

SkillForge is a LangGraph agent that interviews a learner about their skills, identifies gaps through adaptive questioning, generates a personalised learning path, and remembers progress across sessions.

This project exists for one reason: **to build every LangGraph concept from scratch, from a blank file, without following a notebook.**

---

## Why This Is Genuinely AI

- It reasons about skill gaps — not rule-based detection
- It adapts questioning per person — not a static questionnaire
- It generates novel learning paths — not a lookup table
- It remembers across sessions and adapts over time — genuine long-term memory

---

## LangGraph Concept Map

Every concept from Modules 1-6 must appear. Each implementation must be tagged.

| LangGraph Concept | Module | Where Applied in SkillForge |
|------------------|--------|----------------------------|
| StateGraph + TypedDict | 1 | `LearnerState` — carries all state across agents |
| State Reducers | 2 | Parallel nodes merge into single state |
| Conditional edges | 1 | Route based on detected skill level |
| Streaming | 3 | Real-time assessment reasoning to terminal |
| interrupt_before | 3 | Human confirms learning path before saving |
| Dynamic breakpoints | 3 | Escalate if confidence in assessment is low |
| Time Travel | 3 | Replay past assessment session |
| Parallelisation | 4 | Generate multiple learning path options simultaneously |
| Subgraph | 4 | Interview loop as nested subgraph |
| Map-reduce | 4 | Fan out path generation, reduce to ranked recommendation |
| LangGraph Store | 5 | Long-term learner memory — completed topics, pending gaps |
| SqliteSaver | 5 | Persist assessment state across runs |
| Deployment | 6 | LangGraph server or local API endpoint |

---

## Build Sequence — Two Days

### Day 1 — Core Graph (2 hours)

**Stage 1: State Schema (30 min)**
- Define `LearnerState` TypedDict from scratch
- Justify every field — who writes it, who reads it, what reducer
- No code until schema is architecturally sound

**Stage 2: Interview Subgraph (45 min)**
- Build 3-question adaptive interview loop as a nested subgraph
- Conditional routing based on answer quality
- LangGraph concept: Subgraph

**Stage 3: Gap Detection Node (15 min)**
- Consume interview responses
- Identify skill gaps with confidence scores
- LangGraph concept: Conditional edges based on state

**Stage 4: Persistence (30 min)**
- Add SqliteSaver checkpointer
- Resume interrupted assessment across runs
- LangGraph concept: SqliteSaver + thread_id

---

### Day 2 — Intelligence Layer (2 hours)

**Stage 5: Map-Reduce Learning Path (30 min)**
- Fan out — generate 3 learning path options in parallel
- Reduce — rank by fit score, return top recommendation
- LangGraph concept: Map-reduce + Parallelisation

**Stage 6: Human Approval Gate (20 min)**
- Present ranked learning path to learner
- interrupt_before — wait for confirmation or rejection
- LangGraph concept: interrupt_before + update_state

**Stage 7: Long-Term Memory (30 min)**
- LangGraph Store — persist learner profile across sessions
- Track completed topics, pending gaps, session history
- LangGraph concept: LangGraph Store

**Stage 8: Streaming + Time Travel (40 min)**
- Stream assessment reasoning tokens to terminal in real time
- Implement time travel — replay last session state
- LangGraph concept: Streaming + Time Travel

---

## Tech Stack — Zero Cost

| Component | Technology |
|-----------|-----------|
| AI Orchestration | LangGraph |
| LLM | Ollama qwen2.5:7b — local, free |
| Persistence | SqliteSaver |
| Long-term memory | LangGraph Store |
| Embeddings | Not required for v1 |

---

## Repo Structure

```
skillforge/
├── state.py              # LearnerState TypedDict — start here
├── subgraphs/
│   └── interview.py      # Interview subgraph — adaptive questioning
├── nodes/
│   ├── gap_detector.py   # Skill gap identification
│   ├── path_generator.py # Map-reduce learning path generation
│   └── recommender.py    # Final recommendation node
├── memory/
│   ├── sqlite_store.py   # Session persistence
│   └── langgraph_store.py# Long-term learner memory
├── graph.py              # Main StateGraph assembly
├── main.py               # Entry point
└── README.md
```

---

## Definition of Done

- [ ] `LearnerState` schema justified field by field
- [ ] Interview subgraph runs 3 adaptive questions
- [ ] Gap detection produces confidence-scored gaps
- [ ] SqliteSaver persists across terminal restarts
- [ ] Map-reduce generates and ranks 3 learning paths
- [ ] Human approval gate interrupts before saving path
- [ ] LangGraph Store remembers learner across sessions
- [ ] Streaming shows reasoning in real time
- [ ] Time Travel replays last session
- [ ] Every node tagged with LangGraph concept applied
- [ ] Pushed to GitHub with README

---

## Non-Negotiable Rules

- Every architectural decision must be defensible
- Every node must be tagged with the LangGraph concept it applies
- No concept from the module list can be skipped
- Push to GitHub after each stage — not at the end
- State schema must be approved before any node is built