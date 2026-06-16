from error_maps import RECOMMENDATION_INDEX,reverse_error_index
from vector_ops import query_vector_store
from tools_manifest import classify_severity
from langchain_core.tools import tool
from pydantic import BaseModel, Field



@tool
def lookup_known_error_tool(error_signature: str) -> dict:
    """Checks if an isolated error signature string matches a known categorical infrastructure group mapping.
    Falls back to returning 'unknown_exception_set' if no match is found.
    """
    sig_lower = error_signature.lower()

    # Check for direct keyword overlap
    for keyword, category in reverse_error_index.items():
        if keyword in sig_lower:
            obs = {"category": category, "known_match": True, "matched_keyword": keyword}
            # Set the internal state-tracking flag for your LangGraph loop
            obs["_known_match_found"] = True
            return obs

    return {"category": "unknown_exception_set", "known_match": False, "matched_keyword": None}


@tool
def get_infrastructure_fix_tool(category: str) -> str:
    """Returns an actionable recommendation string based on the categorized error."""
    return RECOMMENDATION_INDEX.get(category, RECOMMENDATION_INDEX['unknown_exception_set'])


@tool
def query_vector_store_tool(query_text: str, n_results: int = 2) -> list[str]:
    """Queries the historical ChromaDB log store via semantic vector similarity
    searching to retrieve contextually related historical anomalies."""

    return query_vector_store(query_text, n_results)


@tool
def classify_severity_tool(error_type: str, context: str) -> dict:
    """Tool: Grades risk severity based on error types, targeting OOM as top priority."""
    return classify_severity(error_type, context)


class CompileFinalDiagnosis(BaseModel):
    """Compiles the final triage findings into a strict structured schema for downstream consumption."""

    error_type: str = Field(
        description="The exact exception class or error message signature found."
    )
    root_cause: str = Field(
        description="Detailed explanation of what triggered the primary cascading failure."
    )
    recommendation: str = Field(
        description="Actionable EMR or Spark infrastructure adjustment instructions."
    )
    confidence: float = Field(
        description="Agent confidence score between 0.0 and 1.0."
    )
    escalate_to_human: bool = Field(
        description="True if error category is unknown or confidence is below 0.5"
    )

    class ConfigDict:
        # Enforces the 'additionalProperties': False constraint from your schema
        extra = "forbid"

intermediate_tools = [
    lookup_known_error_tool,
    query_vector_store_tool,
    get_infrastructure_fix_tool,
    classify_severity_tool
]




