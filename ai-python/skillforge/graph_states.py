import uuid
from typing import List, Dict, Any, Literal, Annotated,TypedDict
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
    learner_motivation: str = Field(default="")

    # STAGE 3 fields: The single source of truth for downstream nodes
    detected_gaps: List[str] = Field(default_factory=list)
    gap_confidence_score: float = Field(default=1.0)

    gap_confirmation: Literal["pending", "proceed", "more_questions"] = "pending"
    evaluation_rationale: str = Field(default="")
    gap_confirmation_message: str = Field(default="")

    # Downstream placeholders for future stages
    candidate_learning_paths: Annotated[List[Dict[str, Any]], merge_paths_by_id] = Field(default_factory=list)
    approval_status: Literal["pending", "approved", "rejected"] = "pending"
    ranked_paths: List[Dict[str, Any]] = Field(default_factory=list)
    approved_path: Dict[str, Any] = Field(default_factory=dict)


class SocraticOutputSchema(BaseModel):
    """The structured schema expected from the question generator model turn."""
    next_question: str = Field(
        description="The single Socratic question or one brief Indian parent rejection sentence."
    )
    chosen_subtopic: str = Field(
        description="A concise 1-2 word label representing the core focus area or concept evaluated by this question. Must be extracted strictly from the active user interest domain without referencing examples from the system prompt rules."
    )

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
    max_question: int = Field(default=3)

    covered_subtopics: List[str] = Field(default_factory=list)


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


class EmpatheticRationaleState(BaseModel):
    empathetic_detected_gaps: List[str] = Field(
        description="List of knowledge or skill gaps identified from the learner's responses, phrased in an empathetic, learner-friendly manner."
    )
    empathetic_rationale: str = Field(
        description=(
            "A compassionate, non-judgmental explanation of why these gaps matter for the learner's goals. "
            "It connects the gaps to their interests, career aspirations, or learning journey, and avoids blaming language."
        )
    )
    learner_strengths: List[str] = Field(
        default_factory=list,
        description="Observed strengths or correct understandings demonstrated by the learner during the interaction."
    )




class NotebookUIStateManager:
    """Manages global thread configurations across disparate notebook cells."""
    def __init__(self):
        self.active_config = None

# Instantiate a single global instance of our manager
ui_manager = NotebookUIStateManager()


class LearningPathWorkerState(TypedDict):
    path_idx: int
    learning_vertical: str
    formatted_prompt: str
    candidate_learning_paths: Annotated[List[Dict], operator.add]


class LearningPathOutput(BaseModel):
    focus: str
    plan: List[str]



class RankedLearningPath(BaseModel):
    path_id: str = Field(
        description="Unique identifier of the selected learning path."
    )
    rank: int = Field(
        ge=1,
        le=2,
        description="Recommendation rank."
    )
    score: float = Field(
        ge=0,
        le=100,
        description="Relevance score assigned by the model."
    )
    reason: str = Field(
        description="Why this learning path matches the learner."
    )

class CandidatePathRanking(BaseModel):
    recommended_paths: List[RankedLearningPath] = Field(
        min_length=2,
        max_length=2,
        description="Exactly two best learning path recommendations."
    )



