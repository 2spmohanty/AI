
# Local Multi-Agent Financial Triage Crew
An interactive, agentic application powered by **CrewAI** and **Qwen2.5:7b (via Ollama)**. This project acts as an automated "Bill Shock" and transaction auditor that parses bank data files, extracts complex behavioral anomalies, requests human confirmation, and spits out a structured wealth strategy.

This is a targeted **concept-demonstration project** designed to showcase mastery of all core pillars of the CrewAI framework within a lightweight, local environment.
---

## Core Concepts Demonstrated
This project acts as a functional architectural slice proving expertise across the following **CrewAI** mechanisms:

*   **Multi-Agent Orchestration & Sequential Design:** 3 distinct agents executing specialized tasks in a waterfall data pipeline (`Process.sequential`).
*   **Custom Framework Tools:** Implementation of a native `BaseTool` that dynamically opens, safely reads, and clean-parses physical file streams (`CSVFileExtractorTool`).*   **Structured Output Control:** Forcing the initial AI Agent to output tight, type-validated JSON data mapped to a **Pydantic Schema** instead of unstructured text.*   **Human-In-The-Loop (HITL) Integration:** Pausing execution during intermediate steps to prompt a live operator for input/approval before passing context downstream.
*   **File Persistence Handlers:** Writing the final generated results directly into a persistent local file layout (`auditor_execution_plan.md`).
*   **Privacy-First Local Architectures:** Using an off-grid, fully local open-source LLM (`Ollama/Qwen2.5:7b`) with adjusted inference temperatures.

---  

## System Architecture


```text 
[Target CSV File Input]
        │
        ▼
┌──────────────────────────────────────────────────────┐
│ CREW                                                 │
│                                                      │
│  Agent 1: Data Auditor ──► [Uses Custom CSV Tool]   │
│                              [Forces Pydantic JSON]  │
│        │                                             │
│        ▼                                             │
│  Agent 2: Negotiator ──► [Pauses for Human Input]   │
│        │                                             │
│        ▼                                             │
│  Agent 3: Allocator ──► [Saves markdown to file]    │
└──────────────────────────────────────────────────────┘
        │
        ▼
[auditor_execution_plan.md]
```


---

## Prerequisites & Setup

### 1. Model Preparation (Ollama)
Ensure **Ollama** is running locally on your machine, then pull the target 7B model variant:
```bash
ollama pull qwen2.5:7b
```

### 2. Dependency Management
This project leverages `uv` for lightning-fast workspace environment execution. Ensure you have `crewai` installed:

```bash
uv add crewai
```

---

## How to Run the App

1. Place your target file (e.g., `transac_3.csv`) directly in the project root folder.
2. Ensure the `TARGET_FILE` variable at the bottom of `nugget_crew.py` matches your filename.
3. Boot up the agent loop using `uv run`:

```bash
uv run python nugget_crew.py
```

### What to Expect During the Run
1. **Auditing Phase:** The `Senior Financial Data Auditor` parses the spreadsheet rows, automatically analyzing patterns for pricing spikes, duplicate billing vectors, and frequency volume traps.
2. **Interactive Check:** The loop will freeze at the `Expert Retention & Billing Negotiator`. Look at your terminal! You will see an email draft text block and a direct user prompt: `Please provide feedback:`. Type your feedback or hit **Enter** to skip and approve.
3. **Delivery:** The program will conclude by building a custom financial optimization document in your directory named `auditor_execution_plan.md`.
