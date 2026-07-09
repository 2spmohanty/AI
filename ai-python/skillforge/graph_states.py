import uuid
from typing import List, Dict, Any, Literal, Annotated
from pydantic import BaseModel, Field
import operator
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


def merge_paths_by_id(current: List[Dict[str, Any]], incoming: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Merges incoming paths into current paths based on 'path_id'.
    """
    current_list = current if isinstance(current, list) else []
    incoming_list = incoming if isinstance(incoming, list) else []

    # Merge lists using a dictionary comprehension keyed on path_id (latest wins)
    merged = {path["path_id"]: path for path in (current_list + incoming_list) if "path_id" in path}
    return list(merged.values())


#  Main State

class LearnerProfileState(BaseModel):
    learner: str = Field(default_factory=lambda: str(uuid.uuid4()))
    interests: Annotated[List[str], operator.add] = Field(default_factory=list)
    known_gaps: Annotated[List[str], operator.add] = Field(default_factory=list)
    learning_paths: Annotated[List[str], operator.add] = Field(default_factory=list)



class LearnerState(BaseModel):
    """The unified parent state managing the learner's overall progression."""
    learner_profile: LearnerProfileState = Field(default_factory=LearnerProfileState)

    # Received automatically from the Subgraph output schema
    interview_summary: List[str] = Field(default_factory=list)
    known_gaps: List[str] = Field(default_factory=list)

    # STAGE 3 fields: The single source of truth for downstream nodes
    detected_gaps: List[str] = Field(default_factory=list)
    gap_confidence_score: float = Field(default=1.0)

    # Downstream placeholders for future stages
    candidate_learning_paths: List[Dict[str, Any]] = Field(default_factory=list)
    approval_status: Literal["pending", "approved", "rejected"] = "pending"
    approved_path: Dict[str, Any] = Field(default_factory=dict)


class InterviewSubgraphState(BaseModel):
    """Isolated state container for the chat loop node."""

    learner_profile: LearnerProfileState = Field(default_factory=LearnerProfileState)

    # Correct: Appends new messages to history automatically
    interview_messages: Annotated[list[AnyMessage], add_messages] = Field(default_factory=list)

    subgraph_approval: Literal["pending", "approved", "rejected"] = "pending"

    # FIXED: Removed operator.add so the final node overwrites/sets the definitive report
    known_gaps: List[str] = Field(default_factory=list)
    interview_summary: list[str] = Field(default_factory=list)
    detected_gaps: list[str] = Field(default_factory=list)

    question_asked: int = Field(default=0)
    max_question: int = Field(default=5)


class InterviewSummaryState(BaseModel):
    """The structured schema expected from the LLM output."""
    interview_summary: List[str] = Field(description="Bullet points summarizing the user's overall performance,"
                                                     " mindset, and behavioral patterns during the interview.")
    detected_gaps: List[str] = Field(description="Explicit, clear technical knowledge gaps or misconceptions"
                                                 " identified during the chat.")


class EvaluationState(BaseModel):
    confidence_score: float = Field(description="A confidence score between 0.0 and 1.0. Lower it if the user's "
                                                "answers were vague, evasive, or too brief to make a definitive technical assessment.")
    evaluation_rationale: str = Field(description="A brief sentence explaining why this specific confidence score"
                                                  " was assigned.")