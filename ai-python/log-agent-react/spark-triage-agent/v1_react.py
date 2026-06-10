import json
import re
from openai import OpenAI
from error_maps import lookup_known_error, get_infrastructure_fix
from vector_ops import query_vector_store
from dotenv import load_dotenv
import os
from tools_manifest import classify_severity, extract_error_signature

load_dotenv()
# Initialize your preferred primary LLM orchestration instance

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# --- Agent Tools ---



# -- Response Schemas

INFRA_DIAGNOSTIC_SCHEMA = {
    "name": "final_diagnosis",
    "strict": True,
    "schema": {
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

# --- Manual ReAct Loop System ---

SYSTEM_PROMPT = """
You are a Spark Infrastructure Debugging Agent operating in a strict manual ReAct loop.
You must solve the issue by stepping through: Thought -> Action -> Observation.

Available Tools:
1. lookup_known_error[error_signature] -> Checks if the signature matches a known category map.
2. query_vector_store[query_text] -> Queries historical log database vectors for context.
3. classify_severity[error_type, context] -> Grades risk severity ONLY for OOM errors.

Output Rules:
You must strictly think step-by-step. Use this exact text formatting pattern for your iterations:
Thought: <your logical reasoning here>
Action: <tool_name>[<argument_value>]

The tool result will be injected as [TOOL_RESULT]. You MUST treat it as ground truth.
Do NOT generate, infer, or hallucinate your own Observation. 
If any [TOOL_RESULT] contained "unknown_exception_set", you MUST set confidence below 0.5 and escalate_to_human to true.
Do NOT attempt to resolve unknown errors with confident recommendations.

Once you have gathered sufficient observations and are ready to provide your absolute conclusion, output the string: "STOP_AND_COMPILE"
"""

previous_halucinative_output_rules = """
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

    # 1. Pre-processing pass — extracts the key signature and window bounds deterministically
    signature_result = extract_error_signature(raw_log)
    error_signature = signature_result["error_signature"]
    extracted_context = signature_result["context_summary"]

    # Agent only sees the signature, not the raw log
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Analyze this error signature extracted from an EMR/Spark log:\n{error_signature}"
        }
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
            if tool_name == "lookup_known_error":
                observation_dict = lookup_known_error(tool_arg)
                category = observation_dict.get("category", "unknown_exception_set")
                observation_dict["suggested_recommendation"] = get_infrastructure_fix(category)
            elif tool_name == "query_vector_store":
                observation_dict = {"historical_matches": query_vector_store(tool_arg)}
            elif tool_name == "classify_severity":
                observation_dict = classify_severity(tool_arg, extracted_context)
            else:
                observation_dict = {"error": f"Tool '{tool_name}' does not exist."}
        except Exception as e:
            observation_dict = {"error": f"Execution Error on tool: {str(e)}"}

        observation_json = json.dumps(observation_dict)
        print(f"Observation Injection: {observation_json}")
        ## messages.append({"role": "user", "content": f"Observation: {observation_json}"})
        ## The above line makes the Agent to generate its own observation in case of unknown error.
        messages.append({
            "role": "user",
            "content": f"[TOOL_RESULT] {tool_name} returned: {observation_json}"
        })

    # Final safety compilation if loop breaks early
    fallback_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        response_format={"type": "json_schema", "json_schema": INFRA_DIAGNOSTIC_SCHEMA},
        temperature=0.0
    )
    return json.loads(fallback_response.choices[0].message.content)


