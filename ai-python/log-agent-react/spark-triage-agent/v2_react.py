import os
import json
import re
import anthropic
from error_maps import lookup_known_error, get_infrastructure_fix
from vector_ops import query_vector_store
from v1_react import extract_error_signature, classify_severity
from tools_manifest import ANTHROPIC_TOOLS_MANIFEST
from dotenv import load_dotenv

load_dotenv()

# Initialize official Anthropic SDK client
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

V2_SYSTEM_PROMPT = """
You are an expert EMR/Spark Triage Agent. You analyze error signatures and execution contexts to establish definite structural diagnoses.
Use your tools sequentially to evaluate issues. 

When you have sufficient tool observations, compile your conclusions. 
You must output a single final response that matches this JSON schema exactly:
{
  "error_type": "The technical exception signature found",
  "root_cause": "Detailed architectural root cause analysis statement",
  "recommendation": "Actionable infrastructure modification fix",
  "confidence": 0.0 to 1.0 accuracy evaluation score
}
Provide ONLY the raw JSON object in your final completion block. Do not surround it with markdown blocks.
"""


def run_v2_react_agent(raw_log: str, max_turns: int = 5) -> dict:
    """Executes a production-grade tool use loop via Anthropic, enforcing your strict JSON schema."""

    # 1. Preprocessing sliding window context slider
    signature_result = extract_error_signature(raw_log)
    error_signature = signature_result["error_signature"]
    extracted_context = signature_result["context_summary"]

    messages = [
        {
            "role": "user",
            "content": f"Isolated Target Signature: {error_signature}\nFocused Context Snapshot:\n{extracted_context}"
        }
    ]

    print("Launching v2 Native Anthropic Tool Execution Pipeline...")
    known_match_found = False

    for turn in range(max_turns):
        # On the absolute final turn, force the model to use your diagnostic schema tool
        forcing_final_turn = (turn == max_turns - 1)
        tool_choice = {"type": "tool", "name": "compile_final_diagnosis"} if forcing_final_turn else {"type": "auto"}

        response = client.messages.create(
            model=os.getenv("ANTHROPIC_MODEL"),
            max_tokens=1500,
            system=[{
                "type": "text",
                "text": V2_SYSTEM_PROMPT
            }],
            tools=ANTHROPIC_TOOLS_MANIFEST,
            tool_choice=tool_choice,  # Natively controls tool orchestration constraints
            messages=messages,
            temperature=0.0
        )

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results_content = []

            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_args = block.input
                    tool_call_id = block.id

                    # SUCCESS CRITERIA: The model has filled out  schema
                    if tool_name == "compile_final_diagnosis":
                        print("Final diagnosis compiled via native tool schema enforcement.")
                        final_payload = tool_args
                        if not known_match_found:
                            final_payload["confidence"] = 0.4
                            final_payload["escalate_to_human"] = True

                        # Apply your Safety Escalation Router rules programmatically
                        if final_payload.get("confidence", 1.0) < 0.70 or final_payload.get(
                                "error_type") == "unknown_exception_set":
                            final_payload["escalate_to_human"] = True
                        print(f"[API Action] '{tool_name}'  Result: {final_payload}")
                        return final_payload

                    # Execute intermediate analytical tracking tools
                    print(f"[API Action] Model invoked operational tool '{tool_name}'")
                    observation = {}
                    try:
                        if tool_name == "lookup_known_error":
                            observation = lookup_known_error(tool_args["error_signature"])
                            if observation.get("known_match") == True:
                                known_match_found = True
                            category = observation.get("category", "unknown_exception_set")
                            observation["suggested_recommendation"] = get_infrastructure_fix(category)
                        elif tool_name == "query_vector_store":
                            n_res = tool_args.get("n_results", 2)
                            observation = {
                                "historical_matches": query_vector_store(tool_args["query_text"], n_results=n_res)}
                        elif tool_name == "classify_severity":
                            observation = classify_severity(tool_args["error_type"], tool_args["context"])

                    except Exception as e:
                        observation = {"error": f"Tool processing failure: {str(e)}"}
                    finally:
                        print(f"[API Action] '{tool_name}'  Result: {observation}")

                    tool_results_content.append({
                        "type": "tool_result",
                        "tool_use_id": tool_call_id,
                        "content": json.dumps(observation)
                    })

            messages.append({"role": "user", "content": tool_results_content})

        else:
            # Fallback if text response occurs before tool invocation steps complete
            print("Model exited loop via text signature. Forcing final compilation call...")
            messages.append({"role": "assistant", "content": response.content})
            messages.append(
                {"role": "user", "content": "Generate your final report using the compile_final_diagnosis tool now."})

            forced_response = client.messages.create(
                model=os.getenv("ANTHROPIC_MODEL"),
                max_tokens=1000,
                system=[{
                    "type": "text",
                    "text": V2_SYSTEM_PROMPT
                }],
                tools=ANTHROPIC_TOOLS_MANIFEST,
                tool_choice={"type": "tool", "name": "compile_final_diagnosis"},
                # Forces the schema schema block execution
                messages=messages,
                temperature=0.0
            )

            for block in forced_response.content:
                if block.type == "tool_use" and block.name == "compile_final_diagnosis":
                    return block.input

    return {"error_type": error_signature, "root_cause": "Turn limit reached.", "recommendation": "Escalate manually.",
            "confidence": 0.0, "escalate_to_human": True}
