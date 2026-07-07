from typing import List, Dict, Any, Literal, Annotated
from pydantic import BaseModel, Field


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

class LearnerProfile:
    learner_id: str



class LearnerState(BaseModel):
    """The unified parent state managing the learner's overall progression."""

    learner: LearnerProfile

    candidate_learning_paths: Annotated[List[Dict[str, Any]], merge_paths_by_id] = Field(default_factory=list)
    recommended_learning_paths: List[Dict[str, Any]] = Field(default_factory=list)


    detected_gaps: List[Dict[str, Any]] = Field(default_factory=list)


    approval_status: Literal["pending", "approved", "rejected"] = "pending"


    interview_summary: Dict[str, Any] = Field(default_factory=dict)


class InterviewSubgraphState(BaseModel):
    """Isolated state container for the chat loop node."""

    interview_messages: List[Dict[str, Any]] = Field(default_factory=list)
    current_gap_under_review: Dict[str, Any] = Field(default_factory=dict)

    questions_asked_count: int = 0
    max_questions: int = 5

    subgraph_approval: Literal["pending", "approved", "rejected"] = "pending"
    synthesized_notes: str = ""



