import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Any

JUDGE_PROMPT = """
You are an expert Spark infrastructure engineer.
Given this failure log and an agent's diagnosis, score the diagnosis 1-5.

1 = completely wrong
3 = correct error type, wrong recommendation  
5 = correct error type, correct recommendation, appropriate confidence

Log: {log}
Diagnosis: {diagnosis}
"""


class EvaluationScore(BaseModel):
    """Evaluation score based on diagnostic precision and recommendation quality."""

    score: int = Field(
        description="Score from 1 to 5 based on diagnostic precision and recommendation quality."
    )
    reason: str = Field(
        description="Detailed architectural rationale explaining the given score."
    )

    class ConfigDict:
        # Enforces the 'additionalProperties': False & 'strict': True constraints
        extra = "forbid"



# 1. Initialize the ChatOpenAI client natively
judge_llm = ChatOpenAI(
    model="gpt-5-mini",  # Replaces your placeholder with a powerful structured model
    temperature=0.0
)

# 2. Bind the Pydantic schema to force strict structured generation
structured_judge = judge_llm.with_structured_output(EvaluationScore)


def evaluate_agent_output(log_sample: str, agent_diagnosis: Any) -> EvaluationScore:
    """Evaluates the structural diagnosis quality via OpenAI json_schema Structured Output validation."""

    # Define the template using your exact prompt string
    prompt = ChatPromptTemplate.from_template(JUDGE_PROMPT)

    # Safe checks to read either a standard dictionary or our previous Pydantic class
    if hasattr(agent_diagnosis, "model_dump_json"):
        diagnosis_str = agent_diagnosis.model_dump_json(indent=2)
    elif isinstance(agent_diagnosis, dict):
        import json
        diagnosis_str = json.dumps(agent_diagnosis, indent=2)
    else:
        diagnosis_str = str(agent_diagnosis)

    # Format the inputs safely into LangChain Message structures
    formatted_messages = prompt.format_messages(
        log=log_sample,
        diagnosis=diagnosis_str
    )

    print("Launching LangChain OpenAI Judge Evaluation Pipeline...")

    # 3. Execution returns a true instance of EvaluationScore automatically
    evaluation_result: EvaluationScore = structured_judge.invoke(formatted_messages)

    return evaluation_result
