# AI Engineer Learning Journey

**Smruti Mohanty** · Started May 2026

---

Project board: [Neural Upgrade — Smruti Mohanty](https://github.com/users/2spmohanty/projects/3)

---

## Why I started this

I have spent 19 years building software, infrastructure and data systems. I know how to build things that work at scale. What I did not know was how to build things that think.

That gap bothered me. The world is changing fast and the engineers who will matter in the next decade are the ones who can build intelligent systems — not just reliable ones. I decided to close that gap deliberately, structured, and in public.

This repo is that effort.

---

## What I am building towards

Deep, production-grade knowledge of AI engineering. Not certifications. Not course completions. The ability to take a real problem, design an AI system that solves it, build it, deploy it, and stand behind it.

I am building towards being the kind of engineer who can walk into any room — technical or not — and build something genuinely useful with AI.

---

## My approach

I learn in two layers:

**Concept first** — For each topic I find the sharpest, shortest learning resource available — a DeepLearning.AI short course, a targeted YouTube tutorial, or official documentation. The goal is conceptual clarity in under 90 minutes, not completion certificates.

**Build immediately** — Every concept is reinforced through a focused nugget build — a single Python file that implements one idea cleanly. 30 to 60 minutes. No scaffolding, no tutorials to follow. Just the concept, implemented from memory, with a docstring that explains the decision.

**Capstone at the end** — Every major phase ends with a production-grade project built without tutorials. Something real, something defensible, something that answers a real AI system design interview question.

I track this as a project because I treat it like one. A clear plan, defined phases, measurable progress, and a board I can look at every day to know exactly what to do next.

---

## Progress

| Phase | Topic | Status |
|-------|-------|--------|
| 1 | LLM API Foundations | ✅ Complete |
| 2 | Chaining + Memory (LangChain) | ✅ Complete |
| 3 | RAG + Vector Databases | ✅ Complete |
| 3P | MLOps Zoomcamp | 🟡 In Progress |
| 4 | MCP + Tool Calling | ✅ Complete |
| 5 | AI Agents + LangGraph | ✅ Complete |
| 5B | Multi-Agent Frameworks (CrewAI, ADK) | 🟡 In Progress |
| 5C | Fine-tuning + LoRA | ⬜ Planned |
| 7 | Major Capstones | 🟡 In Progress |
| 8 | AI Safety + Evals | ⬜ Planned |
| 9 | LLMOps + Token Economics | ⬜ Planned |

---

## What I have built

### Log Sentry — EMR Spark Log Triage Agent
> `Phase 1-4` · Python · Anthropic · OpenAI · ChromaDB · LangChain

A multi-version intelligent triage agent that diagnoses Spark/EMR failures from raw logs. Built three times — manual ReAct (v1), Anthropic native tool_use (v2), and LangChain AgentExecutor (v3) — to deeply understand what each abstraction hides.

**What makes it real:** The agent reasons across error signatures, historical ChromaDB patterns, and a known error index to identify root cause — not just pattern-match keywords. Includes LLM-as-judge evaluation, human escalation on unknown errors, and structured JSON output enforcement at the protocol level.

[→ Log Sentry](ai-python/log-agent-react)

---

### PopChoice — Semantic Movie Recommender
> `Phase 3` · Python · FastAPI · Streamlit · Supabase pgvector · OpenAI

A full-stack movie recommendation app using semantic search. Users describe their taste in natural language — the system finds movies by meaning, not keyword match. Production stack: FastAPI backend, Streamlit frontend, Supabase pgvector for embeddings, Docker Compose deployment.

[→ PopChoice](ai-python/popchoice)

---

### SkillForge — AI Self-Assessment and Learning Path Generator
> `Phase 5` · Python · LangGraph · OpenAI · Ollama · LangGraph Studio

A production-grade LangGraph agent covering every module concept from the LangGraph Academy curriculum. Interviews learners through adaptive Socratic questioning, detects knowledge gaps with LLM-as-judge scoring, generates N×3 parallel learning paths via map-reduce, and persists learner profiles across sessions via LangGraph Store. Deployed to LangGraph Studio.

**LangGraph concepts applied:** StateGraph, reducers, subgraphs, map-reduce via `Send()`, `interrupt()`, dynamic breakpoints, Time Travel, SqliteSaver, LangGraph Store, deployment.

[→ SkillForge](ai-python/skillforge)

---

## Key technical decisions made

| Decision | Rationale |
|----------|-----------|
| Build ReAct manually before using frameworks | Cannot debug what you do not understand |
| Anthropic `tool_use` over prompt-based JSON | Protocol-level enforcement beats prompt-level requests |
| ChromaDB local → Supabase pgvector in production | Local for learning, managed for production |
| Ollama for routing, OpenAI for reasoning | Cost efficiency — deterministic routing needs no intelligence |
| `Send()` dispatcher as edge function, not node | Nodes cannot return `Send()` objects — only conditional edge functions |
| LangGraph Store separate from SqliteSaver | Session state vs permanent learner memory are different concerns |
| Nugget builds over mini-projects | Concept depth over project breadth — 30-60 min focused builds beat week-long tutorials |

---



---

*Updated August 2026.*