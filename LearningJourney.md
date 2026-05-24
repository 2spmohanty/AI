# AI Engineer — Learning Journey
**Smruti Mohanty** · Started: May 2026

---

## Progress Dashboard

| Phase | Topic | Status |
|-------|-------|--------|
| 1 | LLM API Foundations | 🟡 In Progress |
| 2 | Chaining + Memory | ⬜ Planned |
| 3 | RAG + Vector Databases | ⬜ Planned |
| 3.P | MLOps Zoomcamp [PARALLEL] | ⬜ Planned |
| 4 | MCP + Tool Calling | ⬜ Planned |
| 5 | AI Agents · LangGraph | ⬜ Planned |
| 6 | Signal + Apply | ⬜ Planned |
| 7 | Major Capstone | ⬜ Planned |

**Legend:** ✅ Done · 🟡 In Progress · ⬜ Planned · ⏭️ Skipped · [PARALLEL] Runs alongside another track

---

## GitHub Portfolio

| # | Project | Phase | Type | Status | Repo |
|---|---------|-------|------|--------|------|
| 1 | AI Practice Scripts | 1 | Practice | ⬜ | — |
| 2 | Karpathy GPT — coded along | 1 | Deep Dive | ⬜ | — |
| 3 | CLI Chatbot (multi-model, streaming) | 1 | Minor Capstone | ⬜ | — |
| 4 | Script Refactoring Tool | 2 | Minor Capstone | ⬜ | — |
| 5 | Log Intelligence System | 3 | Minor Capstone | ⬜ | — |
| 6 | AWS MCP Server | 4 | Minor Capstone | ⬜ | — |
| 7 | Financial Research Agent | 5 | Minor Capstone | ⬜ | — |
| 8 | Major Capstone | 7 | Major Capstone | ⬜ | — |

---

## Skills Tracker

| Skill | Phase | Status | Confidence |
|-------|-------|--------|------------|
| LLM API calls — chat completions | 1 | ✅ | High |
| System / User / Assistant roles | 1 | ✅ | High |
| Async Python with LLM APIs | 1 | ✅ | High |
| Structured outputs — JSON mode | 1 | ✅ | High |
| Pydantic structured outputs | 1 | ✅ | High |
| Nested Pydantic models | 1 | ✅ | High |
| Responses API + web search | 1 | ✅ | High |
| Two-call pipeline: search → structure | 1 | 🟡 | Building |
| HuggingFace Inference API | 1 | ✅ | High |
| Text summarisation | 1 | ✅ | High |
| Text classification + confidence scores | 1 | ✅ | High |
| Local model inference via Ollama | 1 | ⬜ | — |
| transformers pipeline — local | 1 | ⬜ | — |
| Transformer architecture intuition | 1 | ⬜ | — |
| Embedding generation | 4 | ⬜ | — |
| Vector similarity and search | 4 | ⬜ | — |
| Chunking strategies | 3 | ⬜ | — |
| RAG pipeline end-to-end | 3 | ⬜ | — |
| Retrieval evaluation | 3 | ⬜ | — |
| LangChain chains and memory | 2 | ⬜ | — |
| Tool calling — Anthropic API | 4 | ⬜ | — |
| MCP server design and build | 4 | ⬜ | — |
| LangGraph state machines | 5 | ⬜ | — |
| Multi-agent patterns | 5 | ⬜ | — |
| Experiment tracking — MLflow | 3.P | ⬜ | — |
| Model versioning and registry | 3.P | ⬜ | — |
| ML pipeline orchestration | 3.P | ⬜ | — |
| Model serving and monitoring | 3.P | ⬜ | — |

---

---

# PHASE 1 — LLM API Foundations
**Timeline:** Weeks 1–3
**Tracks:** Javascript Track (weekdays) + Python Track (weekdays, mirrors JS) + Deep Dive (weekend)

---

## 1.1 · Javascript Track — Module 1: Intro to AI Engineering
**[SEQUENTIAL]** Complete before 1.2
**Source:** Javascript Track · **Est:** 1 hr 44 min

**Skills gained:** Call LLM APIs · Design prompts · Control model behaviour with parameters · Build AI safety awareness

| # | Lesson | Duration | Done |
|---|--------|----------|------|
| 1 | Welcome to the AI Engineer Path | 4 min | ✅ |
| 2 | AI Engineering basics | 4 min | ✅ |
| 3 | The code so far — tour of starter project | 3 min | ✅ |
| 4 | Polygon API sign-up & key | 2 min | ✅ |
| 5 | Get an OpenAI API key | 2 min | ✅ |
| 6 | Overview of how the API works | 3 min | ✅ |
| 7 | An API call: OpenAI dependency | 3 min | ✅ |
| 8 | An API call: Instance and model | 2 min | ✅ |
| 9 | An API call: The messages array | 6 min | ✅ |
| 10 | A quick word about models | 6 min | ✅ |
| 11 | Prompt Engineering and a challenge | 5 min | ✅ |
| 12 | Adding AI to the App | 5 min | ✅ |
| 13 | Tokens | 6 min | ✅ |
| 14 | Playground | 2 min | ✅ |
| 15 | Temperature | 4 min | ✅ |
| 16 | The Few-Shot Approach | 4 min | ✅ |
| 17 | Adding Examples | 4 min | ✅ |
| 18 | Stop Sequence | 3 min | ✅ |
| 19 | Frequency and Presence Penalties | 3 min | ✅ |
| 20 | Fine-tuning — concepts | 10 min | ✅ |
| 21 | Creating Images with DALL·E 3 API | 11 min | ✅ |
| 22 | Intro to AI Safety | 6 min | ✅ |
| 23 | Safety Best Practices | 3 min | ✅ |
| 24 | Solo Project — PollyGlot | 3 min | ✅ |
| 25 | You made it! | 2 min | ✅ |

---

## 1.2 · Python Track — Module 1 Mirrors
**[PARALLEL with 1.1]** Practice each concept in Python immediately after the JS lesson
**Source:** Python Practice · **Env:** `scrimba-ai-python/` via `uv`

**Skills gained:** Translate LLM API patterns to Python · Use openai + anthropic SDKs · Control async API calls · Port JS exercises independently

| # | Task | Duration | Skills | Done | File |
|---|------|----------|--------|------|------|
| 1.2.1 | Set up .env, load dotenv, print API keys | 15 min | env management | ✅ | — |
| 1.2.2 | Replicate messages array call — openai Python SDK | 20 min | openai SDK, roles | ✅ | — |
| 1.2.3 | Switch to anthropic SDK — same call, different API | 12 min | anthropic SDK | ✅ | — |
| 1.2.4 | Temperature experiment 0→2 — log outputs to file | 20 min | parameters, file I/O | ✅ | — |
| 1.2.5 | Structured output — JSON mode with response_format | 45 min | JSON schema, parsing | ✅ | — |
| 1.2.6 | Pydantic StockReport — beta.chat.completions.parse() | 60 min | Pydantic, typed outputs | ✅ | — |
| 1.2.7 | Nested Pydantic — StockReport + RiskFactors | 30 min | nested models | ✅ | — |
| 1.2.8 | Responses API + web_search_preview tool | 45 min | Responses API | ✅ | — |
| 1.2.9 | Two-call pipeline: search → structure into Pydantic | 60 min | pipeline design | 🟡 | — |
| 1.2.10 | PollyGlot as Python CLI tool | 45 min | argparse, end-to-end | ⬜ | — |

---

## 1.3 · Javascript Track — Module 2: Deploying AI Apps
**[SEQUENTIAL after 1.1]**
**Source:** Javascript Track · **Est:** 50 min
**Status:** ⏭️ Skipped — JS/Cloudflare specific. Python equivalent is FastAPI + Docker + AWS (covered in MLOps phase).

**Key concept retained:** API keys belong server-side. Browser → Backend → OpenAI. Never expose keys in client JS.

| # | Lesson | Duration | Done |
|---|--------|----------|------|
| 1–14 | Cloudflare Workers, Pages, AI Gateway | 50 min | ⏭️ |

---

## 1.4 · Javascript Track — Module 3: Open-Source AI Models
**[SEQUENTIAL after 1.3]**
**Source:** Javascript Track · **Est:** 37 min
**Status:** 🟡 In Progress — JS HuggingFace lessons skipped, Python equivalents done instead.

**Skills gained:** Distinguish open-source vs closed-source models · Choose the right model for cost/privacy tradeoffs · Run models locally without API cost

| # | Lesson | Duration | Done |
|---|--------|----------|------|
| 1 | Open-source vs closed-source | 5 min | ✅ |
| 2 | Intro to HuggingFace.js Inference | 8 min | ⏭️ |
| 3 | Text-to-Speech with HuggingFace.js | 3 min | ⏭️ |
| 4 | Transforming Images with HuggingFace.js | 5 min | ⏭️ |
| 5 | Finding Free Models with HuggingFace Hub | 5 min | ⬜ |
| 6 | AI Models in the Browser with Transformers.js | 7 min | ⏭️ |
| 7 | Download and run AI models locally with Ollama | 4 min | ⬜ |
| 8 | Section Recap | 1 min | ⬜ |

---

## 1.5 · Python Track — Module 3 Mirrors
**[PARALLEL with 1.4]**
**Source:** Python Practice

**Skills gained:** Call HuggingFace Inference API from Python · Run local models via Ollama · Use transformers pipeline · Apply sentiment analysis to financial text

| # | Task | Duration | Skills | Done | File |
|---|------|----------|--------|------|------|
| 1.5.1 | HuggingFace InferenceClient — text summarisation | 30 min | HF API, summarisation | ✅ | — |
| 1.5.2 | Text classification — sentiment with confidence scores | 30 min | classification, scores | ✅ | — |
| 1.5.3 | Run Ollama llama3 locally — Python chat | 20 min | local models, Ollama | ⬜ | — |
| 1.5.4 | Swap OpenAI client → Ollama in structured output code | 30 min | model switching | ⬜ | — |
| 1.5.5 | transformers pipeline — sentiment on 5 financial headlines | 30 min | local inference | ⬜ | — |

---

## 1.6 · Javascript Track — Module 4: Embeddings & Vector Databases
**[SEQUENTIAL after 1.4]**
**Source:** Javascript Track · **Est:** 1 hr 34 min

**Skills gained:** Understand and generate embeddings · Store and query vectors · Build a semantic search system · Understand RAG conceptually

| # | Lesson | Duration | Done |
|---|--------|----------|------|
| 1 | Your next big step in AI engineering | 3 min | ⬜ |
| 2 | What are embeddings? | 6 min | ⬜ |
| 3 | Set up environment variables | 2 min | ⬜ |
| 4 | Create an embedding | 6 min | ⬜ |
| 5 | Challenge: Pair text with embedding | 4 min | ⬜ |
| 6 | Vector databases | 3 min | ⬜ |
| 7 | Set up your vector DB with Supabase | 3 min | ⬜ |
| 8 | Store vector embeddings | 6 min | ⬜ |
| 9 | Semantic search | 5 min | ⬜ |
| 10 | Query embeddings using similarity search | 10 min | ⬜ |
| 11 | Create a conversational response using OpenAI | 8 min | ⬜ |
| 12 | Chunking text from documents | 10 min | ⬜ |
| 13 | Challenge: Split text, get vectors, insert into Supabase | 6 min | ⬜ |
| 14 | Error handling | 3 min | ⬜ |
| 15 | Query database and manage multiple matches | 6 min | ⬜ |
| 16 | AI chatbot proof of concept | 7 min | ⬜ |
| 17 | Retrieval-Augmented Generation (RAG) | 2 min | ⬜ |
| 18 | Solo Project — PopChoice | 5 min | ⬜ |
| 19 | You made it! | 2 min | ⬜ |

---

## 1.7 · Python Track — Module 4 Mirrors
**[PARALLEL with 1.6]**
**Source:** Python Practice

**Skills gained:** Generate and compare embeddings in Python · Build local vector DB with Chroma · Implement full RAG pipeline · Evaluate retrieval quality

| # | Task | Duration | Skills | Done | File |
|---|------|----------|--------|------|------|
| 1.7.1 | Generate embeddings — openai Python SDK | 20 min | text-embedding-3-small | ⬜ | — |
| 1.7.2 | Embed 20 sentences — visualise similarity as heatmap | 45 min | matplotlib, cosine similarity | ⬜ | — |
| 1.7.3 | Vector arithmetic: King − Man + Woman | 20 min | vector space intuition | ⬜ | — |
| 1.7.4 | Chroma local setup — create collection, add, query | 30 min | ChromaDB | ⬜ | — |
| 1.7.5 | Index 30 AWS blog posts — run semantic queries | 60 min | semantic search | ⬜ | — |
| 1.7.6 | Full RAG pipeline over a PDF — Chroma not Supabase | 90 min | RAG end-to-end | ⬜ | — |
| 1.7.7 | Build PopChoice equivalent in Python + Chroma | 60 min | full integration | ⬜ | — |

---

## 1.8 · Javascript Track — Module 5: AI Agents
**[SEQUENTIAL after 1.6]**
**Source:** Javascript Track · **Est:** 1 hr 57 min

**Skills gained:** Design and implement a ReAct agent loop · Define tools and handle function calling · Build an agent that autonomously completes multi-step tasks

| # | Lesson | Duration | Done |
|---|--------|----------|------|
| 1 | AI Agent Intro | 3 min | ⬜ |
| 2 | Prompt Engineering 101 for agents | 6 min | ⬜ |
| 3 | Control Response Formats | 2 min | ⬜ |
| 4 | Zooming Out — what is an agent? | 3 min | ⬜ |
| 5 | Agent Setup | 4 min | ⬜ |
| 6 | Introduction to ReAct prompting | 5 min | ⬜ |
| 7 | Build action functions | 4 min | ⬜ |
| 8 | Write ReAct prompt — part 1 — planning | 3 min | ⬜ |
| 9 | ReAct Agent — part 2 — the prompt | 4 min | ⬜ |
| 10 | ReAct Agent — part 3 — how does the loop work? | 3 min | ⬜ |
| 11 | ReAct Agent — part 4 — code setup | 4 min | ⬜ |
| 12 | ReAct Agent — part 5 — parsing the response | 4 min | ⬜ |
| 13 | ReAct Agent — part 6 — parsing the action | 5 min | ⬜ |
| 14 | ReAct Agent — part 7 — calling the function | 6 min | ⬜ |
| 15 | ReAct Agent — part 8 — housekeeping | 3 min | ⬜ |
| 16 | ReAct Agent — part 9 — the loop | 8 min | ⬜ |
| 17 | OpenAI Functions Agent — part 1 — Intro | 1 min | ⬜ |
| 18 | OpenAI Functions Agent — part 2 — Demo | 2 min | ⬜ |
| 19 | OpenAI Functions Agent — part 3 — Tools | 7 min | ⬜ |
| 20 | OpenAI Functions Agent — part 4 — Loop logic | 2 min | ⬜ |
| 21 | OpenAI Functions Agent — part 5 — Setup challenge | 3 min | ⬜ |
| 22 | OpenAI Functions Agent — part 6 — Tool calls | 7 min | ⬜ |
| 23 | OpenAI Functions Agent — part 7 — Pushing to messages | 4 min | ⬜ |
| 24 | OpenAI Functions Agent — part 8 — Adding arguments | 7 min | ⬜ |
| 25 | OpenAI Functions Agent — part 9 — Automatic calls | 9 min | ⬜ |
| 26 | Adding UI to agent — proof of concept | 4 min | ⬜ |
| 27 | Solo Project — AI Travel Agent | 4 min | ⬜ |
| 28 | Nice work! | 3 min | ⬜ |

---

## 1.9 · Python Track — Module 5 Mirrors
**[PARALLEL with 1.8]**

**Skills gained:** Build a ReAct agent loop from scratch in Python · Use Anthropic tool_use API for function calling · Design tool schemas · Handle tool errors

| # | Task | Duration | Skills | Done | File |
|---|------|----------|--------|------|------|
| 1.9.1 | Build ReAct agent from scratch — Python | 90 min | ReAct loop, parsing | ⬜ | — |
| 1.9.2 | Function-calling agent — Anthropic tool_use API | 60 min | tool_use, tool_result | ⬜ | — |
| 1.9.3 | Build AI Travel Agent in Python with tool calling | 90 min | end-to-end agent | ⬜ | — |

---

## 1.10 · Javascript Track — Module 6: Multimodality
**[SEQUENTIAL after 1.8]**
**Source:** Javascript Track · **Est:** 1 hr 5 min
**Status:** Skim only — DALL·E and Vision covered in Module 1.

**Skills gained:** Use vision models to analyse images · Understand multimodal input patterns

| # | Lesson | Duration | Done |
|---|--------|----------|------|
| 1–10 | Image generation, editing, variations | 53 min | ⏭️ |
| 11 | GPT-4 with Vision — part 1 | 8 min | ⬜ |
| 12 | GPT-4 with Vision — part 2 | 4 min | ⬜ |
| 13 | Recap | 2 min | ⬜ |

---

## 1.11 · Javascript Track — Module 7: OpenAI Assistants API
**[SEQUENTIAL after 1.10]**
**Source:** Javascript Track · **Est:** 30 min

**Skills gained:** Manage stateful multi-turn conversations via threads · Understand Assistants API lifecycle (create → thread → run → poll)

| # | Lesson | Duration | Done |
|---|--------|----------|------|
| 1 | Introducing the Assistants API | 3 min | ⬜ |
| 2 | How assistants work | 4 min | ⬜ |
| 3 | Create an assistant | 6 min | ⬜ |
| 4 | Create a thread and messages | 3 min | ⬜ |
| 5 | Run your assistant | 6 min | ⬜ |
| 6 | Bring it all together | 9 min | ⬜ |
| 7 | More to explore | 1 min | ⬜ |

## 1.12 · Python Track — Module 7 Mirror
**[PARALLEL with 1.11]**

| # | Task | Duration | Skills | Done | File |
|---|------|----------|--------|------|------|
| 1.12.1 | Full Assistants API flow — threads, runs, polling | 40 min | stateful conversations | ⬜ | — |

---

## 1.13 · Javascript Track — Extra: Context Engineering
**[SEQUENTIAL after Module 7]**
**Source:** Javascript Track extras

**Skills gained:** Decide what belongs in a context window · Budget tokens deliberately · Choose between summarisation, sliding window, and retrieval strategies

| # | Topic | Done |
|---|-------|------|
| 1 | What goes in the context window and why | ⬜ |
| 2 | Context window limits and token budgeting | ⬜ |
| 3 | Summarisation vs sliding window vs retrieval | ⬜ |
| 4 | System prompt design for production agents | ⬜ |

---

## 1.14 · Javascript Track — Extra: MCP
**[SEQUENTIAL after Context Engineering]**
**Source:** Javascript Track extras

**Skills gained:** Understand MCP client-server architecture · Distinguish tools, resources, and prompts · Run and inspect an existing MCP server

| # | Topic | Done |
|---|-------|------|
| 1 | MCP concepts — tools, resources, prompts | ⬜ |
| 2 | MCP client-server architecture | ⬜ |
| 3 | Run an existing MCP server locally | ⬜ |
| 4 | Build a simple MCP server | ⬜ |

---

## 1.15 · Deep Dive — Karpathy: Let's Build GPT
**[PARALLEL — one weekend session, any point during Phase 1]**
**Source:** YouTube · Andrej Karpathy · Single video · 2 hr 13 min

**Skills gained:** Understand transformer architecture from first principles · Explain attention, tokens, and context window limits without referring to a course

| # | Task | Done |
|---|------|------|
| 1.15.1 | Watch "Let's build GPT: from scratch, in code, spelled out" | ⬜ |
| 1.15.2 | Code along — bigram language model | ⬜ |
| 1.15.3 | Code along — self-attention mechanism | ⬜ |
| 1.15.4 | Code along — multi-head attention + feedforward | ⬜ |
| 1.15.5 | Write answers in plain English: why next-token prediction? | ⬜ |
| 1.15.6 | Write answers in plain English: what does attention matrix represent? | ⬜ |
| 1.15.7 | Write answers in plain English: why do more layers = smarter? | ⬜ |
| 1.15.8 | Push code + notes to GitHub | ⬜ |

---

## 1.16 · Minor Capstone — Phase 1
**[SEQUENTIAL — after completing 1.1 through 1.12]**
**Build from scratch. No tutorial. Push to GitHub.**

**Skills gained:** Integrate LLM APIs end-to-end · Design a multi-model CLI · Implement streaming and memory from scratch · Write production-quality error handling

### Simple — CLI Chatbot (Python)

| # | Step | Done |
|---|------|------|
| 1.16.1 | Design: system prompt, memory strategy, CLI flags | ⬜ |
| 1.16.2 | Implement base chat loop — openai SDK | ⬜ |
| 1.16.3 | Add streaming output | ⬜ |
| 1.16.4 | Add conversation memory — sliding window 10 turns | ⬜ |
| 1.16.5 | Add --model flag: GPT-4o / Claude / Ollama | ⬜ |
| 1.16.6 | Error handling: rate limits, bad keys, empty responses | ⬜ |
| 1.16.7 | README + push to GitHub | ⬜ |

### Intermediate — Kaggle: NLP Sentiment Dataset
**Dataset:** [To be selected — finance or NLP sentiment]

| # | Step | Done |
|---|------|------|
| 1.16.8 | Load dataset, explore distribution | ⬜ |
| 1.16.9 | Run HuggingFace classifier on 1000 samples | ⬜ |
| 1.16.10 | Compare classifier output vs ground truth labels | ⬜ |
| 1.16.11 | Identify failure cases — where does the model struggle? | ⬜ |
| 1.16.12 | Write findings + push to GitHub | ⬜ |

### Complex — Kaggle: Financial News + Structured Extraction
**Dataset:** [To be selected — financial news corpus]

| # | Step | Done |
|---|------|------|
| 1.16.13 | Load financial news dataset | ⬜ |
| 1.16.14 | Extract structured fields per article via Pydantic | ⬜ |
| 1.16.15 | Chain: extract → classify sentiment → generate summary | ⬜ |
| 1.16.16 | Evaluate: spot-check 20 outputs for accuracy | ⬜ |
| 1.16.17 | Push full pipeline to GitHub | ⬜ |

---
---

# PHASE 2 — Chaining + Memory
**Timeline:** Weeks 4–5
**Source:** DeepLearning.AI — Harrison Chase & Andrew Ng

---

## 2.1 · LangChain for LLM Application Development
**[SEQUENTIAL]**
**Source:** DeepLearning.AI (free) · **Est:** 5 hrs

**Skills gained:** Chain multiple LLM calls with typed I/O · Manage conversation memory across session types · Route user intent to different processing paths · Evaluate LLM output quality programmatically

| # | Module | Est. Time | Done |
|---|--------|-----------|------|
| 2.1.1 | Models, Prompts & Parsers | 60 min | ⬜ |
| 2.1.2 | Memory for LLMs | 60 min | ⬜ |
| 2.1.3 | Chains — sequential, router | 60 min | ⬜ |
| 2.1.4 | Q&A over Documents | 60 min | ⬜ |
| 2.1.5 | Evaluation & Agents | 60 min | ⬜ |

---

## 2.2 · Python Track — LangChain Practice
**[PARALLEL with 2.1]**

**Skills gained:** Build typed LangChain pipelines · Implement and compare memory strategies · Evaluate LLM outputs with QAEvalChain

| # | Task | Duration | Skills | Done | File |
|---|------|----------|--------|------|------|
| 2.2.1 | PromptTemplate → ChatOpenAI → PydanticOutputParser | 45 min | LangChain basics | ⬜ | — |
| 2.2.2 | Compare 3 memory types on same conversation | 60 min | memory strategies | ⬜ | — |
| 2.2.3 | 3-step intent router chain | 45 min | RouterChain | ⬜ | — |
| 2.2.4 | Load 3 Python files — Q&A over your own code | 45 min | RetrievalQA | ⬜ | — |
| 2.2.5 | Evaluate CLI chatbot — 10 Q&A pairs + QAEvalChain | 60 min | LLM evaluation | ⬜ | — |

---

## 2.3 · Minor Capstone — Phase 2
**[SEQUENTIAL — after 2.1 and 2.2]**

**Skills gained:** Design a multi-step LangChain pipeline · Handle structured I/O across chained calls · Present diff-style output for real engineering use cases

### Simple — Chain 3 prompts: summarise → critique → improve

| # | Step | Done |
|---|------|------|
| 2.3.1 | Summarise a technical doc with LLMChain | ⬜ |
| 2.3.2 | Critique the summary — identify gaps | ⬜ |
| 2.3.3 | Improve the summary using critique as context | ⬜ |
| 2.3.4 | Push to GitHub | ⬜ |

### Intermediate — Kaggle: Text dataset Q&A with memory

| # | Step | Done |
|---|------|------|
| 2.3.5 | Select a Kaggle text dataset | ⬜ |
| 2.3.6 | Build RetrievalQA chain over dataset | ⬜ |
| 2.3.7 | Add ConversationSummaryMemory — multi-turn Q&A | ⬜ |
| 2.3.8 | Evaluate 10 Q&A pairs — accuracy check | ⬜ |
| 2.3.9 | Push to GitHub | ⬜ |

### Complex — Script Refactoring Tool

| # | Step | Done |
|---|------|------|
| 2.3.10 | Chain step 1: Analyse — what does this code do? | ⬜ |
| 2.3.11 | Chain step 2: Identify — list specific issues | ⬜ |
| 2.3.12 | Chain step 3: Refactor — rewrite it | ⬜ |
| 2.3.13 | Chain step 4: Explain — what changed and why | ⬜ |
| 2.3.14 | Output: side-by-side diff with difflib | ⬜ |
| 2.3.15 | Test on 3 real Python scripts from career | ⬜ |
| 2.3.16 | Add --model flag — compare GPT-4o vs Claude | ⬜ |
| 2.3.17 | Push to GitHub with before/after README | ⬜ |

---
---

# PHASE 3 — RAG + Vector Databases
**Timeline:** Weeks 6–8
**Source:** Pinecone Academy + Local Chroma

---

## 3.1 · Embeddings Deep Dive
**[SEQUENTIAL]**
**Source:** Pinecone Academy · **Est:** 4 hrs

**Skills gained:** Explain embedding geometry · Choose the right embedding model · Measure and compare semantic similarity · Detect failure modes in retrieval

| # | Topic | Done |
|---|-------|------|
| 3.1.1 | What are embeddings — geometric intuition | ⬜ |
| 3.1.2 | Cosine similarity, dot product, Euclidean — when to use which | ⬜ |
| 3.1.3 | Embedding models: text-embedding-3-small vs all-MiniLM | ⬜ |
| 3.1.4 | Embed 20 sentences — visualise as similarity heatmap | ⬜ |
| 3.1.5 | Vector arithmetic: King − Man + Woman | ⬜ |

---

## 3.2 · Chroma Local Setup
**[SEQUENTIAL after 3.1]**
**Est:** 3 hrs

**Skills gained:** Set up and operate a local vector database · Store, filter, and retrieve by metadata · Choose between persistent and in-memory collections

| # | Task | Done |
|---|------|------|
| 3.2.1 | Install Chroma: uv add chromadb | ⬜ |
| 3.2.2 | Create persistent collection, add documents, query | ⬜ |
| 3.2.3 | Filter by metadata — timestamp, severity, service | ⬜ |
| 3.2.4 | Index 30 AWS blog posts — run 10 semantic queries | ⬜ |
| 3.2.5 | Compare semantic search vs keyword search on same queries | ⬜ |

---

## 3.3 · RAG Pipeline Architecture
**[SEQUENTIAL after 3.2]**
**Est:** 5 hrs

**Skills gained:** Design chunking strategies for different content types · Build end-to-end RAG pipeline · Evaluate retrieval quality with metrics · Debug retrieval failures systematically

| # | Topic | Done |
|---|-------|------|
| 3.3.1 | Fixed-size chunking — when it works, when it breaks | ⬜ |
| 3.3.2 | Semantic chunking — split at natural boundaries | ⬜ |
| 3.3.3 | RecursiveCharacterTextSplitter in LangChain | ⬜ |
| 3.3.4 | Same PDF — 3 chunking strategies — measure retrieval hit rate | ⬜ |
| 3.3.5 | RetrievalQA chain — build full Q&A over 50-page PDF | ⬜ |
| 3.3.6 | Hybrid search: BM25 keyword + semantic | ⬜ |
| 3.3.7 | Re-ranking retrieved chunks | ⬜ |
| 3.3.8 | Parent-document retrieval — small chunks, large context | ⬜ |
| 3.3.9 | Evaluate 10 Q&A pairs — measure accuracy | ⬜ |

---

## 3.4 · Minor Capstone — Phase 3
**[SEQUENTIAL — after 3.1 through 3.3]**

**Skills gained:** Apply RAG to real operational data · Debug retrieval failures with an eval framework · Document findings as a professional case study

### Simple — Kaggle: Document Q&A

| # | Step | Done |
|---|------|------|
| 3.4.1 | Select a Kaggle text/document dataset | ⬜ |
| 3.4.2 | Chunk, embed, store in Chroma | ⬜ |
| 3.4.3 | Q&A interface — 10 natural language queries | ⬜ |
| 3.4.4 | Push to GitHub | ⬜ |

### Intermediate — Kaggle: Finance News RAG

| # | Step | Done |
|---|------|------|
| 3.4.5 | Select financial news Kaggle dataset | ⬜ |
| 3.4.6 | Chunk by article — embed + store in Chroma | ⬜ |
| 3.4.7 | Q&A: "What was said about Amazon in Q1 2024?" | ⬜ |
| 3.4.8 | Evaluate 10 pairs — accuracy check | ⬜ |
| 3.4.9 | Push to GitHub | ⬜ |

### Complex — Log Intelligence System

| # | Step | Done |
|---|------|------|
| 3.4.10 | Collect 100+ real VMware/AWS logs from career | ⬜ |
| 3.4.11 | Write log parser: timestamp, severity, service, message | ⬜ |
| 3.4.12 | Chunk + embed all logs into persistent Chroma collection | ⬜ |
| 3.4.13 | Build CLI: natural language queries with source attribution | ⬜ |
| 3.4.14 | Write 10 evaluation Q&A pairs with known answers | ⬜ |
| 3.4.15 | Run eval — measure accuracy, identify failures | ⬜ |
| 3.4.16 | Debug + fix chunking until >80% accuracy | ⬜ |
| 3.4.17 | Write findings doc + push to GitHub | ⬜ |

---

## 3.P · MLOps Zoomcamp
**[PARALLEL — runs on weekends during Phase 3 and Phase 4]**
**Source:** DataTalks.Club MLOps Zoomcamp (free) · **Est:** 8–10 weeks part-time

**Skills gained:** Track and compare experiments systematically · Version models and datasets · Build automated ML pipelines · Serve models as APIs · Monitor model drift in production

| # | Module | Est. Time | Done |
|---|--------|-----------|------|
| 3.P.1 | Module 1: Introduction to MLOps | 2 hrs | ⬜ |
| 3.P.2 | Module 2: Experiment tracking — MLflow | 4 hrs | ⬜ |
| 3.P.3 | Module 3: Orchestration — Prefect / Mage | 4 hrs | ⬜ |
| 3.P.4 | Module 4: Model deployment — batch, web service, streaming | 4 hrs | ⬜ |
| 3.P.5 | Module 5: Model monitoring — Evidently | 4 hrs | ⬜ |
| 3.P.6 | Module 6: Best practices — CI/CD, testing, linting | 3 hrs | ⬜ |
| 3.P.7 | Zoomcamp project — deploy a model end-to-end | 6 hrs | ⬜ |

---
---

# PHASE 4 — MCP + Tool Calling
**Timeline:** Weeks 9–10
**Source:** MCP Docs · Anthropic API · FastMCP

---

## 4.1 · Anthropic Tool Use API
**[SEQUENTIAL]**
**Est:** 4 hrs

**Skills gained:** Design tool schemas in JSON · Handle the tool_use / tool_result lifecycle · Build multi-tool agents · Prevent and handle tool errors

| # | Task | Done |
|---|------|------|
| 4.1.1 | Read Anthropic tool use docs — concepts and schema format | ⬜ |
| 4.1.2 | Define a tool in Python as a JSON schema dict | ⬜ |
| 4.1.3 | Handle tool_use content blocks in response | ⬜ |
| 4.1.4 | Execute tool, return tool_result to API | ⬜ |
| 4.1.5 | Calculator tool — LLM decides when to use it vs answer directly | ⬜ |
| 4.1.6 | Multi-tool agent: weather + calculator + unit converter | ⬜ |

---

## 4.2 · MCP Protocol
**[SEQUENTIAL after 4.1]**
**Est:** 3 hrs

**Skills gained:** Read and understand the MCP specification · Distinguish tools, resources, and prompts in MCP · Set up and run an MCP server locally

| # | Task | Done |
|---|------|------|
| 4.2.1 | Read MCP specification at modelcontextprotocol.io | ⬜ |
| 4.2.2 | MCP server anatomy: tools, resources, prompts | ⬜ |
| 4.2.3 | Run an existing MCP server locally — Filesystem MCP | ⬜ |
| 4.2.4 | Install FastMCP: uv add fastmcp | ⬜ |
| 4.2.5 | Build Hello World MCP server with 2 tools | ⬜ |

---

## 4.3 · Minor Capstone — Phase 4
**[SEQUENTIAL — after 4.1 and 4.2]**

**Skills gained:** Build a production-quality MCP server · Connect LLM to real AWS infrastructure · Enable natural language infrastructure queries · Document IAM requirements for real deployment

### Simple — MCP server with 2 mock tools

| # | Step | Done |
|---|------|------|
| 4.3.1 | Design 2 tools: get_weather, convert_currency | ⬜ |
| 4.3.2 | Implement in FastMCP with mock data | ⬜ |
| 4.3.3 | Test with Claude Desktop | ⬜ |
| 4.3.4 | Push to GitHub | ⬜ |

### Intermediate — Kaggle: Data exploration via tool-calling agent

| # | Step | Done |
|---|------|------|
| 4.3.5 | Select a tabular Kaggle dataset | ⬜ |
| 4.3.6 | Build tools: load_data, describe_column, plot_distribution | ⬜ |
| 4.3.7 | Agent explores dataset via tool calls — natural language | ⬜ |
| 4.3.8 | Push to GitHub | ⬜ |

### Complex — AWS MCP Server

| # | Step | Done |
|---|------|------|
| 4.3.9 | Set up FastMCP project structure + pyproject.toml | ⬜ |
| 4.3.10 | Tool 1: list_instances — boto3 EC2 describe | ⬜ |
| 4.3.11 | Tool 2: get_metrics — CloudWatch get_metric_data | ⬜ |
| 4.3.12 | Tool 3: search_logs — CloudWatch filter_log_events | ⬜ |
| 4.3.13 | Tool 4: estimate_cost — Cost Explorer | ⬜ |
| 4.3.14 | Error handling + IAM permissions guide | ⬜ |
| 4.3.15 | Test with Claude Desktop — natural language infra queries | ⬜ |
| 4.3.16 | README with architecture diagram + push to GitHub | ⬜ |

---
---

# PHASE 5 — AI Agents · LangGraph
**Timeline:** Weeks 11–13
**Source:** LangChain Academy

---

## 5.1 · LangGraph Fundamentals
**[SEQUENTIAL]**
**Est:** 4 hrs

**Skills gained:** Design state machines for AI workflows · Use conditional edges for decision logic · Implement persistence and checkpointing · Add human-in-the-loop approval steps

| # | Topic | Done |
|---|-------|------|
| 5.1.1 | Why graphs beat chains — cycles and state | ⬜ |
| 5.1.2 | StateGraph, nodes, edges — the building blocks | ⬜ |
| 5.1.3 | TypedDict state schema — strong typing | ⬜ |
| 5.1.4 | Conditional edges — decision logic in graphs | ⬜ |
| 5.1.5 | ToolNode — integrate tools into graph nodes | ⬜ |
| 5.1.6 | Human-in-the-loop: interrupts before/after nodes | ⬜ |
| 5.1.7 | Persistence: SqliteSaver and MemorySaver | ⬜ |
| 5.1.8 | Practice: 3-node graph — research → draft → review | ⬜ |
| 5.1.9 | Practice: agent with tool + human approval interrupt | ⬜ |

---

## 5.2 · Advanced Agent Patterns
**[SEQUENTIAL after 5.1]**
**Est:** 4 hrs

**Skills gained:** Build self-correcting agents · Design retry and fallback logic · Architect multi-agent supervisor/worker systems · Run agents in parallel

| # | Topic | Done |
|---|-------|------|
| 5.2.1 | Handling tool errors inside graph nodes | ⬜ |
| 5.2.2 | Retry edges with exponential backoff | ⬜ |
| 5.2.3 | Validation nodes — check output before proceeding | ⬜ |
| 5.2.4 | Practice: self-correcting agent — 3 retries before failing | ⬜ |
| 5.2.5 | Supervisor + worker architecture | ⬜ |
| 5.2.6 | Passing state between sub-graphs | ⬜ |
| 5.2.7 | Parallel nodes — run agents concurrently | ⬜ |
| 5.2.8 | Practice: supervisor routes to research vs writing agent | ⬜ |

---

## 5.3 · Minor Capstone — Phase 5
**[SEQUENTIAL — after 5.1 and 5.2]**

**Skills gained:** Integrate all prior skills into a working multi-step agent · Build a self-critiquing loop · Apply RAG retrieval inside an agent graph · Ship a demo-ready project

### Simple — 3-node agent: search → summarise → format

| # | Step | Done |
|---|------|------|
| 5.3.1 | Web search node — Tavily or DuckDuckGo | ⬜ |
| 5.3.2 | Summarise node — structured Pydantic output | ⬜ |
| 5.3.3 | Format node — produce clean Markdown report | ⬜ |
| 5.3.4 | Push to GitHub | ⬜ |

### Intermediate — Kaggle: Multi-step data analysis agent

| # | Step | Done |
|---|------|------|
| 5.3.5 | Select a finance/tabular Kaggle dataset | ⬜ |
| 5.3.6 | Agent: load → explore → hypothesise → verify → report | ⬜ |
| 5.3.7 | Self-critique loop: if report is incomplete, re-run explore | ⬜ |
| 5.3.8 | Push to GitHub | ⬜ |

### Complex — Financial Research Agent

| # | Step | Done |
|---|------|------|
| 5.3.9 | Design graph: search → retrieve → draft → critique → format | ⬜ |
| 5.3.10 | Node 1: web_search — Tavily API | ⬜ |
| 5.3.11 | Node 2: rag_retrieve — connect Phase 3 Chroma | ⬜ |
| 5.3.12 | Node 3: draft — combine sources into research summary | ⬜ |
| 5.3.13 | Node 4: critique — score draft against 4 criteria | ⬜ |
| 5.3.14 | Conditional edge: loop if score < 7, max 3 attempts | ⬜ |
| 5.3.15 | Node 5: format — final Markdown report | ⬜ |
| 5.3.16 | Test on AAPL, NVDA, CBA.AX, ANZ.AX, BHP.AX | ⬜ |
| 5.3.17 | Record 2-minute Loom demo | ⬜ |
| 5.3.18 | Push to GitHub + LinkedIn post | ⬜ |

---
---

# PHASE 6 — Signal + Apply
**Timeline:** Weeks 14–16

---

## 6.1 · Portfolio Consolidation
**[SEQUENTIAL]**

| # | Task | Done |
|---|------|------|
| 6.1.1 | All GitHub repos — add architecture diagrams to READMEs | ⬜ |
| 6.1.2 | Record a 2-minute demo for each major project | ⬜ |
| 6.1.3 | Update LinkedIn — skills, projects, posts | ⬜ |
| 6.1.4 | Update resume for AI Engineer / Forward Deployment roles | ⬜ |

## 6.2 · Open Source Contribution
**[PARALLEL with 6.1]**

**Skills gained:** Navigate a large open-source codebase · Submit a PR to a recognised AI repo · Build a public commit history in the AI ecosystem

| # | Task | Done |
|---|------|------|
| 6.2.1 | Pick a repo: LangChain / LlamaIndex / FastMCP | ⬜ |
| 6.2.2 | Find a good first issue | ⬜ |
| 6.2.3 | Submit PR — documentation, bug fix, or small feature | ⬜ |
| 6.2.4 | PR merged | ⬜ |

## 6.3 · Job Applications

| # | Task | Done |
|---|------|------|
| 6.3.1 | Target list: 10 companies across FinTech + AI companies | ⬜ |
| 6.3.2 | First 5 applications sent | ⬜ |
| 6.3.3 | Interview prep: system design for AI systems | ⬜ |
| 6.3.4 | Interview prep: explain RAG, agents, MCP without slides | ⬜ |

---
---

# PHASE 7 — Major Capstone
**Timeline:** After Phase 5 complete · Duration: open-ended
**Note:** The problem to solve here is deliberately left open. By the time Phase 5 is done, the most interesting problem to solve will be clearer than it is today. What is recorded here is the minimum structure — the actual domain and features get defined then.

---

## 7.1 · Problem Definition
**[SEQUENTIAL — do not start until Phase 5 is complete]**

| # | Task | Done |
|---|------|------|
| 7.1.1 | Define the problem: what does this tool solve and for whom? | ⬜ |
| 7.1.2 | Define the user: who uses it, what do they know, what do they need? | ⬜ |
| 7.1.3 | Define the AI layer: which capabilities from Phases 1–5 does this use? | ⬜ |
| 7.1.4 | Define the data layer: what data flows in, out, and through? | ⬜ |
| 7.1.5 | Architecture diagram: frontend → backend → LLM → data stores | ⬜ |
| 7.1.6 | Tech stack decision: which open-source tools, which enterprise APIs? | ⬜ |
| 7.1.7 | MVP definition: smallest version that demonstrates the core value | ⬜ |

## 7.2 · Build — MVP

| # | Layer | Done |
|---|-------|------|
| 7.2.1 | Backend: FastAPI application skeleton | ⬜ |
| 7.2.2 | LLM layer: integrate with chosen models | ⬜ |
| 7.2.3 | Data layer: ingestion pipeline | ⬜ |
| 7.2.4 | Data layer: transformation + processing | ⬜ |
| 7.2.5 | Data layer: egress to target stores | ⬜ |
| 7.2.6 | Agent layer: orchestration with LangGraph | ⬜ |
| 7.2.7 | Frontend: CLI first, UI second | ⬜ |
| 7.2.8 | MLOps: experiment tracking + monitoring (from Phase 3.P) | ⬜ |

## 7.3 · Ship

| # | Task | Done |
|---|------|------|
| 7.3.1 | Deploy MVP — containerised, cloud-hosted | ⬜ |
| 7.3.2 | Internal testing — run against real data | ⬜ |
| 7.3.3 | Documentation: architecture, setup, usage | ⬜ |
| 7.3.4 | Public GitHub release | ⬜ |
| 7.3.5 | Write-up: what it does, how it works, what you learned | ⬜ |

---

