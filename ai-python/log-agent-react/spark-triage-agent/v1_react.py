import json
import re
from openai import OpenAI
from error_maps import lookup_known_error, get_infrastructure_fix
from vector_ops import query_vector_store
from dotenv import load_dotenv
import os

load_dotenv()
# Initialize your preferred primary LLM orchestration instance

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# --- Agent Tools ---

def extract_error_signature(log_text: str) -> dict:
    """Tool: Uses regex to isolate core exception profiles from raw log lines."""
    pattern = re.compile(r'([a-zA-Z0-9_.]+Exception|Error:.*?)(?=\s|\||$)')
    matches = pattern.findall(log_text)
    sig = matches[-1] if matches else log_text.split('|')[0]
    return {"error_signature": sig.strip()}


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


# -- Response Schemas

INFRA_DIAGNOSTIC_SCHEMA = {
    "name": "final_diagnosis",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "error_type": {"type": "string", "description": "The exact exception class or error message signature found."},
            "root_cause": {"type": "string", "description": "Detailed explanation of what triggered the primary cascading failure."},
            "recommendation": {"type": "string", "description": "Actionable EMR or Spark infrastructure adjustment instructions."},
            "confidence": {"type": "number", "description": "Agent confidence score between 0.0 and 1.0."}
        },
        "required": ["error_type", "root_cause", "recommendation", "confidence"],
        "additionalProperties": False
    }
}

# Schema for the Judge/Evaluation Prompt
JUDGE_SCORE_SCHEMA = {
    "name": "evaluation_score",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "score": {
                "type": "integer",
                "description": "Score from 1 to 5 based on diagnostic precision and recommendation quality."
            },
            "reason": {
                "type": "string",
                "description": "Detailed architectural rationale explaining the given score."
            }
        },
        "required": ["score", "reason"],
        "additionalProperties": False
    }
}

# --- Manual ReAct Loop System ---

SYSTEM_PROMPT = """
You are a Spark Infrastructure Debugging Agent operating in a strict manual ReAct loop.
You must solve the issue by stepping through: Thought -> Action -> Observation.

Available Tools:
1. extract_error_signature[log_text] -> Simplifies dirty log strings to a core exception.
2. lookup_known_error[error_signature] -> Checks if the signature matches a known category map.
3. query_vector_store[query_text] -> Queries historical log database vectors for context.
4. classify_severity[error_type, context] -> Grades risk severity ONLY for OOM errors.

Output Rules:
You must strictly think step-by-step. Use this exact text formatting pattern for your iterations:
Thought: <your logical reasoning here>
Action: <tool_name>[<argument_value>]
Observation: <this space will be populated with the tool output injection>

Once you have gathered sufficient observations and are ready to provide your absolute conclusion, output the string: "STOP_AND_COMPILE"
"""

# --- MANUAL react agent

def run_v1_react_agent(raw_log: str, max_iterations: int = 5) -> dict:
    """Executes a manual text-parsing string loop driving the ReAct pattern, finalized with a Structured Output schema."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Analyze this EMR/Spark error log chunk and determine the root cause:\n{raw_log}"}
    ]

    print("Launching v1 Manual ReAct Loop...")

    for i in range(max_iterations):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.0
        )

        assistant_text = response.choices[0].message.content
        print(f"\n[Iteration {i + 1}] Processing Step:\n{assistant_text}")
        messages.append({"role": "assistant", "content": assistant_text})

        # Check if the model signals it has completed its investigation steps
        if "STOP_AND_COMPILE" in assistant_text or i == (max_iterations - 1):
            print("\nLoop complete. Compiling structured final answer...")

            # Send a final prompt using Structured Outputs to guarantee your strict JSON payload format
            messages.append(
                {"role": "user", "content": "Compile your findings into the required structural JSON format now."})
            final_structured_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                response_format={"type": "json_schema", "json_schema": INFRA_DIAGNOSTIC_SCHEMA},
                temperature=0.0
            )
            return json.loads(final_structured_response.choices[0].message.content)

        # Parse out the Tool call using string processing
        action_match = re.search(r'Action:\s*(\w+)\[(.*?)\]', assistant_text, re.DOTALL)
        if not action_match:
            print("ReAct loop failed to format action string cleanly. Forcing structured fallback compilation.")
            break

        tool_name, tool_arg = action_match.groups()
        tool_arg = tool_arg.strip().strip('"').strip("'")

        # Execute the selected tool
        observation_dict = {}
        try:
            if tool_name == "extract_error_signature":
                observation_dict = extract_error_signature(tool_arg)
            elif tool_name == "lookup_known_error":
                observation_dict = lookup_known_error(tool_arg)
                category = observation_dict.get("category", "unknown_exception_set")
                observation_dict["suggested_recommendation"] = get_infrastructure_fix(category)
            elif tool_name == "query_vector_store":
                observation_dict = {"historical_matches": query_vector_store(tool_arg)}
            elif tool_name == "classify_severity":
                observation_dict = classify_severity(tool_arg, raw_log)
            else:
                observation_dict = {"error": f"Tool '{tool_name}' does not exist."}
        except Exception as e:
            observation_dict = {"error": f"Execution Error on tool: {str(e)}"}

        observation_json = json.dumps(observation_dict)
        print(f"Observation Injection: {observation_json}")
        messages.append({"role": "user", "content": f"Observation: {observation_json}"})

    # Final safety compilation if loop breaks early
    fallback_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        response_format={"type": "json_schema", "json_schema": INFRA_DIAGNOSTIC_SCHEMA},
        temperature=0.0
    )
    return json.loads(fallback_response.choices[0].message.content)

# --- Evaluation Judge Framework ---

JUDGE_PROMPT = """
You are an expert Spark infrastructure engineer.
Given this failure log and an agent's diagnosis, score the diagnosis 1-5.

1 = completely wrong
3 = correct error type, wrong recommendation  
5 = correct error type, correct recommendation, appropriate confidence

Log: {log}
Diagnosis: {diagnosis}
"""

def evaluate_agent_output(log_sample: str, agent_diagnosis: dict) -> dict:
    """Evaluates the structural diagnosis quality via OpenAI json_schema Structured Output validation."""
    diagnosis_str = json.dumps(agent_diagnosis)
    response = client.chat.completions.create(
        model="gpt-5-mini",  # Using a larger model for accurate grading/evaluation
        messages=[{"role": "user", "content": JUDGE_PROMPT.format(log=log_sample, diagnosis=diagnosis_str)}],
        response_format={"type": "json_schema", "json_schema": JUDGE_SCORE_SCHEMA}
    )
    return json.loads(response.choices[0].message.content)
