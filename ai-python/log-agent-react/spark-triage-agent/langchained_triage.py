from langchain.agents import create_agent
from langchain_anthropic import ChatAnthropic

from tools_manifest import ANTHROPIC_TOOLS_MANIFEST, extract_error_signature
from dotenv import load_dotenv
import anthropic
import os
from error_maps import lookup_known_error, get_infrastructure_fix
from vector_ops import query_vector_store
from v1_react import extract_error_signature, classify_severity
import json
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
import os
import json
from typing import List
from langchain_triage_tools import (lookup_known_error_tool,
    query_vector_store_tool,
    get_infrastructure_fix_tool,
    classify_severity_tool,CompileFinalDiagnosis)
load_dotenv()


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

llm = ChatAnthropic(model=os.getenv("ANTHROPIC_MODEL"), temperature=0.0,max_tokens=1500)

structured_llm = llm.with_structured_output(CompileFinalDiagnosis)



def run_lang_chained_v2(raw_log: str, max_turns: int = 5) -> CompileFinalDiagnosis:
    """Executes a production-grade tool use loop natively in standard LangChain,

    guaranteeing a Pydantic object return format.
    """
    signature_result = extract_error_signature(raw_log)
    error_signature = signature_result["error_signature"]
    extracted_context = signature_result["context_summary"]

    messages: List[BaseMessage] = [
        HumanMessage(
            content=f"Isolated Target Signature: {error_signature}\nFocused Context Snapshot:\n{extracted_context}"
        )
    ]

    print("Launching LangChain Anthropic Tool Execution Pipeline...")
    known_match_found = False

    # We only expose the intermediate operational tools during the loop execution
    intermediate_tools = [lookup_known_error_tool, query_vector_store_tool, classify_severity_tool]

    for turn in range(max_turns):
        execution_messages = [("system", V2_SYSTEM_PROMPT)] + messages

        # Check if we are forced into the absolute final evaluation turn
        forcing_final_turn = (turn == max_turns - 1)

        if forcing_final_turn:
            print("Force-breaking loop to compile final strict diagnosis...")
            break  # Exit the loop to fall through to the strict Pydantic extractor below

        # Otherwise, let the model think and use intermediate tools normally
        model_with_tools = llm.bind_tools(intermediate_tools)
        response = model_with_tools.invoke(execution_messages)
        messages.append(response)

        if response.tool_calls:
            tool_messages = []
            tool_map = {t.name: t for t in intermediate_tools}

            for tool_call in response.tool_calls:
                name = tool_call["name"]
                args = tool_call["args"]
                call_id = tool_call["id"]

                print(f"[API Action] Model invoked operational tool '{name}'")
                try:
                    if name == "lookup_known_error_tool":
                        observation = tool_map[name].invoke(args)
                        if observation.get("known_match"):
                            known_match_found = True
                        category = observation.get("category", "unknown_exception_set")
                        observation["suggested_recommendation"] = get_infrastructure_fix(category)

                    elif name == "query_vector_store_tool":
                        res = tool_map[name].invoke(args)
                        observation = {"historical_matches": res}

                    elif name == "classify_severity_tool":
                        observation = tool_map[name].invoke(args)
                except Exception as e:
                    observation = {"error": f"Tool processing failure: {str(e)}"}

                tool_messages.append(ToolMessage(
                    content=json.dumps(observation),
                    tool_call_id=call_id,
                    name=name
                ))

            messages.extend(tool_messages)
        else:
            # If the model didn't call any tools, it means it is ready to give the answer
            print("Model completed its analysis steps early. Transitioning to compilation...")
            break

    # =====================================================================
    # FINAL STRUCTURED EXTRACTION (Guarantees Pydantic Object)
    # =====================================================================
    print("Enforcing strict Pydantic schema formatting via with_structured_output...")

    # Inject a guiding prompt to make sure it fills out the schema using the gathered context
    messages.append(HumanMessage(content="Compile your final triage findings into the requested schema now."))

    # This invocation is guaranteed to return a true instance of CompileFinalDiagnosis (Pydantic)
    final_payload: CompileFinalDiagnosis = structured_llm.invoke([("system", V2_SYSTEM_PROMPT)] + messages)

    # Apply your conditional downstream business safety rules onto the Pydantic instance attributes
    if not known_match_found:
        final_payload.confidence = 0.4
        final_payload.escalate_to_human = True

    if final_payload.confidence < 0.70 or final_payload.error_type == "unknown_exception_set":
        final_payload.escalate_to_human = True

    print(f"[API Complete] Structured Output Generated Successfully: {type(final_payload)}")
    return final_payload



