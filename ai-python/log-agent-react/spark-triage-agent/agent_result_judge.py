import os
import json
import time
from openai import OpenAI


# Initialize the OpenAI Client for the Judge / Evaluator Pipeline
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Configuration & Schema Declarations ---

JUDGE_PROMPT = """
You are an expert Spark infrastructure engineer.
Given this failure log and an agent's diagnosis, score the diagnosis 1-5.

1 = completely wrong
3 = correct error type, wrong recommendation  
5 = correct error type, correct recommendation, appropriate confidence

Log: {log}
Diagnosis: {diagnosis}
"""

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


# --- Core Evaluator Function ---

def evaluate_agent_output(log_sample: str, agent_diagnosis: dict) -> dict:
    """Evaluates the structural diagnosis quality via OpenAI json_schema Structured Output validation."""
    diagnosis_str = json.dumps(agent_diagnosis)
    response = openai_client.chat.completions.create(
        model="gpt-5-mini",  # Using a larger model for accurate grading/evaluation
        messages=[{"role": "user", "content": JUDGE_PROMPT.format(log=log_sample, diagnosis=diagnosis_str)}],
        response_format={"type": "json_schema", "json_schema": JUDGE_SCORE_SCHEMA}
    )
    return json.loads(response.choices[0].message.content)




