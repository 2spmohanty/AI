import re

ANTHROPIC_TOOLS_MANIFEST = [
    {
        "name": "lookup_known_error",
        "description": "Checks if an isolated error signature string matches a known categorical infrastructure group mapping. Falls back to returning 'unknown_exception_set' if no match is found.",
        "input_schema": {
            "type": "object",
            "properties": {
                "error_signature": {
                    "type": "string",
                    "description": "The exact isolated exception class pattern or error signature string (e.g., 'java.lang.OutOfMemoryError')."
                }
            },
            "required": ["error_signature"],
            "additionalProperties": False
        }
    },
    {
        "name": "query_vector_store",
        "description": "Queries the historical ChromaDB log store via semantic vector similarity searching to retrieve contextually related historical anomalies.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query_text": {
                    "type": "string",
                    "description": "The target error message string used to calculate the vector distance mapping profile."
                },
                "n_results": {
                    "type": "integer",
                    "description": "Total number of context log documents to return from the database. Defaults to 2."
                }
            },
            "required": ["query_text"],
            "additionalProperties": False
        }
    },
    {
        "name": "classify_severity",
        "description": "Grades infrastructure failure severity risk profiles, prioritizing Out of Memory (OOM) tracking locations while mapping secondary failures explicitly.",
        "input_schema": {
            "type": "object",
            "properties": {
                "error_type": {
                    "type": "string",
                    "description": "The classified exception class name or extracted categorical signature."
                },
                "context": {
                    "type": "string",
                    "description": "The immediate sliding window context (50 lines before, 100 lines after) to evaluate system component positioning (e.g., driver vs executor)."
                }
            },
            "required": ["error_type", "context"],
            "additionalProperties": False
        }
    },
    {
        "name": "compile_final_diagnosis",
        "description": "Compiles the final triage findings into a strict structured schema for downstream consumption.",
        "input_schema": {
        "type": "object",
        "properties": {
            "error_type": {"type": "string",
                           "description": "The exact exception class or error message signature found."},
            "root_cause": {"type": "string",
                           "description": "Detailed explanation of what triggered the primary cascading failure."},
            "recommendation": {"type": "string",
                               "description": "Actionable EMR or Spark infrastructure adjustment instructions."},
            "confidence": {"type": "number", "description": "Agent confidence score between 0.0 and 1.0."},
            "escalate_to_human": {
                "type": "boolean",
                "description": "True if error category is unknown or confidence is below 0.5"
            }
        },
        "required": ["error_type", "root_cause", "recommendation", "confidence","escalate_to_human"],
        "additionalProperties": False
    }
    }

]

ANTHROPIC_TOOLS_WITHOUT_VECTOR_MANIFEST = [
    {
        "name": "lookup_known_error",
        "description": "Checks if an isolated error signature string matches a known categorical infrastructure group mapping. Falls back to returning 'unknown_exception_set' if no match is found.",
        "input_schema": {
            "type": "object",
            "properties": {
                "error_signature": {
                    "type": "string",
                    "description": "The exact isolated exception class pattern or error signature string (e.g., 'java.lang.OutOfMemoryError')."
                }
            },
            "required": ["error_signature"],
            "additionalProperties": False
        }
    },
    {
        "name": "classify_severity",
        "description": "Grades infrastructure failure severity risk profiles, prioritizing Out of Memory (OOM) tracking locations while mapping secondary failures explicitly.",
        "input_schema": {
            "type": "object",
            "properties": {
                "error_type": {
                    "type": "string",
                    "description": "The classified exception class name or extracted categorical signature."
                },
                "context": {
                    "type": "string",
                    "description": "The immediate sliding window context (50 lines before, 100 lines after) to evaluate system component positioning (e.g., driver vs executor)."
                }
            },
            "required": ["error_type", "context"],
            "additionalProperties": False
        }
    },
    {
        "name": "compile_final_diagnosis",
        "description": "Compiles the final triage findings into a strict structured schema for downstream consumption.",
        "input_schema": {
        "type": "object",
        "properties": {
            "error_type": {"type": "string",
                           "description": "The exact exception class or error message signature found."},
            "root_cause": {"type": "string",
                           "description": "Detailed explanation of what triggered the primary cascading failure."},
            "recommendation": {"type": "string",
                               "description": "Actionable EMR or Spark infrastructure adjustment instructions."},
            "confidence": {"type": "number", "description": "Agent confidence score between 0.0 and 1.0."},
            "escalate_to_human": {
                "type": "boolean",
                "description": "True if error category is unknown or confidence is below 0.5"
            }
        },
        "required": ["error_type", "root_cause", "recommendation", "confidence","escalate_to_human"],
        "additionalProperties": False
    }
    }

]

def extract_error_signature(log_text: str) -> dict:
    """
    Finds the primary error signature using an optimized regex pattern,
    and grabs a targeted context window (50 lines before, 100 lines after)
    to capture driver vs executor locations without inflating tokens.
    """
    # 1. Split the raw multi-line log string into an iterable array of individual lines
    lines = log_text.splitlines()

    # 2. Compile your refined regex pattern that captures the full exception line cleanly
    pattern = re.compile(r'([a-zA-Z0-9_.]+(?:Traceback|Exception|Error)[^\n]*)')

    target_index = -1
    matched_sig = ""

    # Iterate forward to find the first occurence of an error
    for idx in range(len(lines)):
        match = pattern.search(lines[idx])
        if match:
            target_index = idx
            matched_sig = match.group(0).strip()
            break

    # Fallback — no Exception/Error keyword found in any line
    # Default to first line as best available signal
    if target_index == -1:
        matched_sig = lines[0].strip() if lines else "Unknown Error Signature"
        target_index = 0

    # 3. Calculate targeted sliding window boundaries around the failure anchor point
    # 50 lines prior to capture upstream initialization or infrastructure triggers
    start_window = max(0, target_index - 50)
    # 100 lines after to capture full stacked trace responses and secondary drops
    end_window = min(len(lines), target_index + 101)

    # Extract lines and join them back using standard delimiters
    surrounding_context_lines = lines[start_window:end_window]
    context_summary = "\n".join(surrounding_context_lines)

    return {
        "error_signature": matched_sig,
        "context_summary": context_summary
    }


def classify_severity(error_type: str, context: str) -> dict:
    """Tool: Grades risk severity based on error types, targeting OOM as top priority."""
    ctx_lower = context.lower()
    err_lower = error_type.lower()

    # Check for Out Of Memory conditions first
    is_oom = any(kw in err_lower or kw in ctx_lower for kw in ["oom", "out of memory", "heap space", "overhead limit"])
    if is_oom:
        if "driver" in ctx_lower:
            return {
                "severity": "CRITICAL",
                "impact": "Driver node crash terminates the entire Spark application context immediately."
            }
        return {
            "severity": "HIGH",
            "impact": "Executor node memory exhaustion slows down data processing and causes task retries."
        }

    # Grade alternative operational categories explicitly
    if any(kw in err_lower for kw in ["access", "denied", "permission", "token"]):
        return {
            "severity": "HIGH",
            "impact": "Security or credential failure prevents job initialization or target resource read/write operations."
        }
    elif any(kw in err_lower for kw in ["timeout", "timed out"]):
        return {
            "severity": "MEDIUM",
            "impact": "Network latency or high GC pauses causing communication drops between system coordinators."
        }
    elif any(kw in err_lower for kw in ["schema", "incompatible", "merge"]):
        return {
            "severity": "MEDIUM",
            "impact": "Data structural format mismatch forcing processing pipeline execution halts."
        }

    # Catch-all fallback for generic framework warnings or unknown exceptions
    return {
        "severity": "LOW",
        "impact": "Standard framework anomaly, non-fatal exception footprint, or background worker retry."
    }

