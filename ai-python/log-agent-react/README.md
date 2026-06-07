
# Automated EMR/Spark Log Triage Agent: Technical Architecture Document

## Project Objective

The ABC engineering ecosystem executes high-throughput distributed workflows generating over 10,000 internal Apache Spark job failures weekly across production Amazon EMR clusters. Manual L1 triage currently consumes approximately 2 engineering hours per team member daily. This process relies on repetitive tasks: parsing multi-line Java/Scala stack traces, matching signatures to legacy runbooks, and routing escalations.
This project implements an Automated Log Triage Agent designed to ingest raw Spark/YARN container failure logs and output an instantly actionable, schema-enforced diagnostic payload.

![logsentry.png](../images/logsentry.png)

                        
------------------------------
## Technical KPIs & Implementation Targets
This project evaluates two structural variations of the agent loop:

* v1: Manual ReAct (Deterministic Iteration): Built using an explicit string-parsing text loop driven by gpt-5-mini. It acts as a transparent, auditable state machine where tool selection is extracted via regular expressions.
* v2: Native Tool Use (Production Grade): Leverages Anthropic’s structured tool_use schema arrays to enforce strict JSON compliance at the model compilation boundary.

------------------------------
## System Constraints & Engineering Guards

### 1. Latency Profile

* Target: Interactive diagnostic generation must resolve in under 10 seconds.
* Design Pattern: Heavy context preparation—including text token chunking and categorical dictionary lookups—runs in local memory before calling the model endpoint.

### 2. Context Windows & Token Budgets

* Target: Strict 2,000 input tokens max per inference loop call.
* Design Pattern: Raw log payloads often exceed 50KB. The system uses LangChain’s RecursiveCharacterTextSplitter combined with keyword-filtering rules to strip clean INFO lines. This preserves only critical exception signatures, preventing token bloat.

### 3. Accuracy & Guardrails

* Target: Zero ungrounded predictions (hallucinations).
* Design Pattern: If a signature does not match records in the local ChromaDB database or your custom error index maps, the model outputs unknown_exception_set.

### 4. Integration Specifications

* Target: At least one tool execution per diagnostic loop.
* Design Pattern: The agent interacts with four functional hooks:
* extract_error_signature() (Isolates error signatures using regex pattern matching).
   * lookup_known_error() (Checks your static error categories and fetches runbook solutions).
   * query_vector_store() (Searches historical logs in ChromaDB using local cosine similarity).
   * classify_severity() (Evaluates infrastructure risks, focusing on driver vs. executor OOM issues).

### 5. Downstream Target Schema

* Target: Clean JSON response strings matching downstream logging systems.
* Design Pattern: The system uses OpenAI Structured Outputs (json_schema) to guarantee the final payload always returns four exact fields:

{
  "error_type": "string",
  "root_cause": "string",
  "recommendation": "string",
  "confidence": 0.0
}


### 6. Safety Escalation Router

* Target: Safe routing of uncertain errors.
* Design Pattern: If the agent's confidence falls below 0.70 (70%), the pipeline triggers an alert flag. This stops automated fixes and safely escalates the traceback to a human engineer.


### Constraints

- **Latency:** A triage result must return in under 10 seconds for interactive use. Async is fine for batch.
- **Cost:** Cannot send full 50KB log files to the LLM. Token budget per call: ~2,000 input tokens max.
- **Accuracy:** The agent must *not* hallucinate a root cause. Unknown = unknown. It must say so.
- **Tool use:** The agent must use at least one tool call (not just a prompt). Think about what tools a real triage agent would need.
- **Output schema:** The response must be structured JSON, not free text. Downstream systems consume it.
- **Safety:** If the agent is >70% uncertain, it must route to a human. No silent failures.

---

## PRIMARY ERROR CATEGORIES

| # | Type | Root Cause Signal |
|---|------|-------------------|
| 1 | OOM | Heap exhaustion → cascade |
| 2 | S3 Access Denied | 403 on first read attempt |
| 3 | Schema Mismatch | decimal/string on `total_amount` |
| 4 | Lost Executor | RPC disassociation |
| 5 | Task Timeout | TaskKilled after 120000ms |

---


## INGESTION

```mermaid

sequenceDiagram
    autonumber
    actor Dev as Developer / execution context
    participant ING as ingestion::ingest_log_file
    participant VOPS_P as vector_ops::parse_log
    participant LC as LangChain (RecursiveCharacterTextSplitter)
    participant CHROMA as ChromaDB Collection
    participant HF_HUB as Hugging Face Hub (Cloud Cache)

    Note over Dev, ING: Phase 1: Ingestion Trigger
    Dev->>ING: Calls with ("path/to/spark_executor.log")
    ING->>VOPS_P: Passes filepath to extraction engine
    
    Note over VOPS_P, LC: Phase 2: Structural Clean & Smart Chunking
    VOPS_P->>VOPS_P: Reads file into memory & runs fast CRITICAL_KEYWORDS scan
    alt 0 Anomaly Footprints Identified
        VOPS_P-->>ING: Returns empty list []
        ING-->>Dev: Logs "Skipping file: No error footprints detected."
    else Error Keywords Present
        VOPS_P->>LC: Sends raw log text string to text_splitter.create_documents()
        Note over LC: LangChain splits logs safely using separators [\n, " | ", " "]
        LC-->>VOPS_P: Returns list of LangChain Document objects (< 1200 chars each)
    end

    Note over VOPS_P, CHROMA: Phase 3: Metadata Extraction & Schema Mapping
    loop For Each LangChain Document Chunk
        VOPS_P->>VOPS_P: Regex extracts Timestamp & Log Level (ERROR/WARN)
        VOPS_P->>VOPS_P: Drops standard INFO text fragments to eliminate vector noise
        VOPS_P->>VOPS_P: Compiles entry mapping into Chroma standard {"id", "document", "metadata"}
    end
    VOPS_P-->>ING: Returns list of formatted candidate dictionaries

    Note over ING, HF_HUB: Phase 4: Vector Generation & Storage Ingestion
    rect rgb(30, 40, 50)
        ING->>CHROMA: Calls collection.upsert(ids, documents, metadatas)
        Note over CHROMA: Chroma intercepts text fields via hf_embedding_fn
        CHROMA->>HF_HUB: Requests mathematical token vector arrays (Checks local cache first)
        HF_HUB-->>CHROMA: Returns 384-dimensional dense float vector embeddings
        CHROMA->>CHROMA: Indexes arrays into local disk using Cosine Similarity Distance Model
    end
    
    CHROMA-->>ING: Upsert transactional confirmation
    ING-->>Dev: Logs "Successfully ingested X anomaly segments."

```

---


## AGENT FLOW

```mermaid
sequenceDiagram
    autonumber
    actor Load Log main.py
    participant V1 as v1_react::run_v1_react_agent
    participant OAI as OpenAI (gpt-5-mini)
    participant MAPS as error_maps::lookup_known_error
    participant V_OPS as vector_ops::query_vector_store
    participant V1_SEV as v1_react::classify_severity
    participant V1_SIG as v1_react::extract_error_signature
    participant JUDGE as v1_react::evaluate_agent_output
    participant OAI_G5 as OpenAI (gpt-5)

    %% Phase 1: Execution Initialization
    Note over Dev, V1: Phase 1: Diagnostics Initialization
    Dev->>V1: Calls with (raw_log, max_iterations)
    
    %% Phase 2: ReAct Core Analytical Processing Loop
    rect rgb(30, 40, 50)
        Note over V1, OAI: Phase 2: ReAct Thought-Action-Observation Loop (Up to max_iterations)
        loop Continuous Iterations
            V1->>OAI: Submits Message Stack to determine next Action
            OAI-->>V1: Returns Thought and Selected Action String
            
            alt Action contains 'extract_error_signature'
                V1->>V1_SIG: Executed locally using Regex processing
                V1_SIG-->>V1: Returns {"error_signature": sig}
            else Action contains 'lookup_known_error'
                V1->>MAPS: Matches signature against static mappings
                MAPS-->>V1: Returns {"category": cat, ...} 
                Note over V1, MAPS: Calls error_maps::get_infrastructure_fix inside step logic
            else Action contains 'query_vector_store'
                V1->>V_OPS: Submits raw query text parameter
                V_OPS-->>V1: Returns {"historical_matches": [...]}
            else Action contains 'classify_severity'
                V1->>V1_SEV: Evaluates log context for risk tiers
                V1_SEV-->>V1: Returns {"severity": tier, "impact": text}
            end
            
            V1->>V1: Appends Result as an 'Observation' token to messages context
        end
    end

    %% Phase 3: Extraction and Compiling Final State
    Note over V1, OAI: Phase 3: Structured Answer Compilation
    V1->>OAI: Enforces closure pass ("STOP_AND_COMPILE") with FINAL_ANSWER_SCHEMA
    OAI-->>V1: Returns verified structured diagnostic JSON dictionary
    V1-->>Dev: Sends structured final analysis object payload back to primary process

    %% Phase 4: Verification and Judging Pipeline
    Note over Dev, OAI_G5: Phase 4: Verification Judging Phase
    Dev->>JUDGE: Calls with (raw_log, diagnosis_dict)
    JUDGE->>OAI_G5: Submits JUDGE_PROMPT & JUDGE_SCORE_SCHEMA (No Temperature)
    OAI_G5-->>JUDGE: Returns validated integer score and text rationale JSON object
    JUDGE-->>Dev: Delivers final evaluation audit report dictionary

```