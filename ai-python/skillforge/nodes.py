from typing import Any, Dict
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.errors import GraphInterrupt
from langgraph.types import interrupt, Command, Send
from langgraph.checkpoint.memory import MemorySaver

from langgraph.store.base import BaseStore
import hashlib




from graph_states import (InterviewSubgraphState, InterviewSummaryState,
                          LearnerState, EvaluationState, SocraticOutputSchema, EmpatheticRationaleState,
                          LearningPathWorkerState, LearningPathOutput)

from prompts import (INTERVIEWER_PROMPT, SUMMARIZATION_SYSTEM_PROMPT, BROADER_CONCEPT_WORKER_PROMPT,
                     JOB_READINESS_WORKER_PROMPT, LEARN_BY_DOING_WORKER_PROMPT, LOW_CONFIDENT_GAP_CONFIRMATION_PROMPT,
                     CONFIDENT_GAP_CONFIRMATION_PROMPT, RATIONALE_HUMANIZER_PROMPT, EVALUATION_PROMPT,
                     LEARNING_PATH_RANKER_PROMPT)

from models import question_model, general_model, eval_model




from graph_states import CandidatePathRanking
import json


# LangGraph Concept: Subgraph State Reading — Dynamically analyzes runtime user interests and gaps to generate a single, progressively complex Socratic question without providing direct answers.
def QuestionGeneratorNode(state: InterviewSubgraphState) -> Dict[str, Any]:
    learner = state.learner_profile
    user_interests = learner.interests if learner and learner.interests else ["General Engineering"]
    chat_history = state.interview_messages or []

    # Format the lists directly so they are hyper-visible to the attention window
    already_covered = ", ".join(state.covered_subtopics) if state.covered_subtopics else "None yet"

    system_prompt = INTERVIEWER_PROMPT.format(
        user_interest=", ".join(user_interests),
        known_gaps=state.known_gaps,
        detected_gaps=state.detected_gaps,
        covered_subtopics=already_covered  # Hard data injection
    )

    # Force strict schema mapping
    dynamic_model = question_model.with_structured_output(SocraticOutputSchema)
    messages = [SystemMessage(content=system_prompt)] + chat_history

    response: SocraticOutputSchema = dynamic_model.invoke(messages)

    # Return the message to message history and append the subtopic to the tracking ledger
    return {
        "interview_messages": [AIMessage(content=response.next_question)],
        "covered_subtopics": [response.chosen_subtopic]  # Appends via list configuration
    }


# LangGraph Concept: Inline Interruptions — Executes an inline interrupt() that freezes the graph engine to asynchronously capture user text responses from the notebook interface.
def follow_up_node(state: InterviewSubgraphState) -> Dict[str, Any]:
    #  Executes an inline interrupt() that freezes the graph engine to asynchronously capture user text responses from the notebook interface.
    last_question = state.interview_messages[-1].content if state.interview_messages else "Please respond:"

    user_input = interrupt(last_question)  # # Triggers a programmatic pause and broadcasts out of the graph.
    cleaned_input = str(user_input).strip()
    question_asked = state.question_asked
    max_question = state.max_question
    next_question_count = question_asked + 1

    if cleaned_input.upper() in ["N", "NO", "EXIT", "DONE"] or next_question_count >= max_question:
        return {"question_asked": next_question_count, "subgraph_approval": "approved"}

    return {
        "interview_messages": [HumanMessage(content=cleaned_input)],
        "question_asked": next_question_count,
        "subgraph_approval": "pending"
    }


# LangGraph Concept: Subgraph State Output Mapping — Runs a single-turn structured extraction task at the subgraph's boundary to map the final chat summary and raw gaps up to the parent graph.
def summarisation_node(state: InterviewSubgraphState) -> Dict[str, Any]:
    # Runs a single-turn structured extraction task at the subgraph's boundary to map the final chat summary and raw gaps up to the parent graph.

    chat_history = state.interview_messages or []

    summary_model = general_model.with_structured_output(InterviewSummaryState)

    messages = [SystemMessage(content=SUMMARIZATION_SYSTEM_PROMPT)] + chat_history

    structured_response: InterviewSummaryState = summary_model.invoke(messages)

    return {
        "interview_summary": structured_response.interview_summary,
        "detected_gaps": structured_response.detected_gaps
    }


# LangGraph Concept: Conditional Edges & Dynamic Breakpoints — Functions as an LLM-as-a-Judge validation gate that triggers a mid-node dynamic breakpoint if the interview data confidence score drops below the safety threshold.
def evaluation_node(learner_state: LearnerState) -> LearnerState:
    known_gaps = learner_state.known_gaps or []
    detected_gaps = learner_state.detected_gaps
    interview_summary = learner_state.interview_summary

    evaluation_model = eval_model.with_structured_output(EvaluationState)
    formatted_prompt = EVALUATION_PROMPT.format(
        transcript_summary=interview_summary,
        known_gaps=known_gaps,
        detected_gaps=detected_gaps
    )

    messages = [SystemMessage(content=formatted_prompt)]
    evaluation_response: EvaluationState = evaluation_model.invoke(messages)

    # Build humanised message and save to state ──
    empathetic_model = general_model.with_structured_output(EmpatheticRationaleState)

    humanized = empathetic_model.invoke([
        SystemMessage(content=RATIONALE_HUMANIZER_PROMPT.format(
            conversation_summary=interview_summary,
            detected_gaps=detected_gaps,
            raw_rationale=evaluation_response.evaluation_rationale
        ))
    ])

    strength = ", ".join(humanized.learner_strengths) if humanized.learner_strengths else "Your engagement and effort"
    if evaluation_response.confidence_score > 0.8:
        humanised_msg = CONFIDENT_GAP_CONFIRMATION_PROMPT.format(
            strength=strength,
            gaps="\n".join(f"  • {g}" for g in humanized.empathetic_detected_gaps),
            rationale=humanized.empathetic_rationale
        )
    else:
        humanised_msg = LOW_CONFIDENT_GAP_CONFIRMATION_PROMPT.format(
            strength=strength,
            gaps="\n".join(f"  • {g}" for g in humanized.empathetic_detected_gaps),
            rationale=humanized.empathetic_rationale
        )

    return {
        "gap_confidence_score": evaluation_response.confidence_score,
        "evaluation_rationale": evaluation_response.evaluation_rationale,
        "gap_confirmation_message": humanised_msg,
    }


# LangGraph Concept: Inline Interruptions — Pauses the parent execution layout to ask the human learner for structural confirmation of their detected gaps using humanized AI rationale.
def gap_confirmation_node(state: LearnerState) -> Dict[str, Any]:
    # LangGraph Concept: Inline Interruptions

    human_response = interrupt(
        "🤖 Mentor: " + state.gap_confirmation_message + "\n\nKindly answer with:\n"
                                                        "YES/AGREE: To proceed with a learning path or\n"
                                                        "MORE/RETRY: For answering more questions."
    )

    response = str(human_response).strip().upper()

    if any(keyword in response for keyword in ["YES", "DONE", "CONFIRM", "PROCEED", "OK", "SURE"]):
        return {"gap_confirmation": "proceed"}

    if any(keyword in response for keyword in ["MORE", "NO", "CONTINUE", "AGAIN", "RETRY"]):
        return {"gap_confirmation": "more_questions"}

    # Fallback — unexpected input, re-interrupt with same message
    return {"gap_confirmation": "pending"}


VERTICALS = {
    "BROADER_CONCEPT": (
        "Focus on the bigger picture: how this concept connects to other ideas, "
        "why it matters in the ecosystem, and how it fits into the learner's overall understanding."
    ),
    "JOB_READINESS": (
        "Focus on career and interview relevance: how this skill is used in real jobs, "
        "what interviewers expect, and how the learner can present and apply it in a professional context."
    ),
    "LEARN_BY_DOING": (
        "Focus on hands-on practice: coding exercises, mini-projects, debugging tasks, "
        "or experiments that reinforce the concept through active doing and iteration."
    ),
}


def learning_path_dispatcher(state: LearnerState):
    return [Send("learning_path_worker", {
        "path_idx": idx,
        "learning_vertical": vertical,
        "formatted_prompt": prompt[vertical].format(
            vertical_description=VERTICALS[vertical],
            target_gap=target_gap,
            evaluation_rationale=state.evaluation_rationale,
            conversation_summary=state.interview_summary,
            learner_profile=state.interview_summary
        )
    }) for idx, target_gap in enumerate(state.detected_gaps) for vertical in VERTICALS]


prompt = {}
prompt["BROADER_CONCEPT"] = BROADER_CONCEPT_WORKER_PROMPT
prompt["JOB_READINESS"] = JOB_READINESS_WORKER_PROMPT
prompt["LEARN_BY_DOING"] = LEARN_BY_DOING_WORKER_PROMPT


def learning_path_worker(state: dict):
    worker_model = general_model.with_structured_output(LearningPathOutput)
    response = worker_model.invoke([SystemMessage(content=state["formatted_prompt"])])
    return {"candidate_learning_paths": [{
        "path_id": f"{state['learning_vertical']}_{state['path_idx']}",
        "focus": response.focus,
        "plan": response.plan
    }]}




def check_gap_confirmation_gate(state: LearnerState) -> str:
    if state.gap_confirmation == "proceed":
        return learning_path_dispatcher(state)
    elif state.gap_confirmation == "more_questions":
        return "interview_loop"
    else:
        return "gap_confirmation_node"


def candidate_path_node(state: LearnerState) -> Dict[str, Any]:
    interests = state.learner_profile.interests
    motivation = state.learner_motivation
    learning_paths: dict = state.candidate_learning_paths

    system_prompt = LEARNING_PATH_RANKER_PROMPT.format(
        interests=interests,
        motivation=motivation,
        learning_paths=json.dumps(learning_paths, indent=2)
    )
    structured_llm = eval_model.with_structured_output(CandidatePathRanking)
    response = structured_llm.invoke([SystemMessage(content=system_prompt)])

    return {"ranked_paths": [r.model_dump() for r in response.recommended_paths]}





def learning_path_approval_node(state: LearnerState, store: BaseStore) -> Dict[str, Any]:
    learner_id = state.learner_profile.learner
    ranked_paths = state.ranked_paths or []
    all_paths = {p["path_id"]: p for p in state.candidate_learning_paths}
    # Build the display message
    path_lines = []
    for path in ranked_paths:
        full = all_paths.get(path.get("path_id"), {})
        steps = "\n".join(f"   • {s}" for s in full.get("plan", []))
        path_lines.append(
            f"PATH ID: {path.get('path_id')}\n"
            f"RANK: {path.get('rank')} | SCORE: {path.get('score')}/100\n"
            f"WHY: {path.get('reason')}\n"
            f"FOCUS: {full.get('focus', '')}\n"
            f"PLAN:\n{steps}"
        )

    paths_block = "\n\n".join(path_lines) if path_lines else "No paths available."

    choice_message = f"""
Choose one of the paths that is best suited for your learning.

{paths_block}

Please type the **PATH ID** you want to continue with.
"""

    # 2) Interrupt to surface the message & wait for user choice
    # The value passed to interrupt is what your client / Send API will receive.
    user_choice = interrupt(choice_message)

    # 3) Match the user's choice back to the ranked_paths
    selected_id = str(user_choice).strip()

    if selected_id.upper() in ["EXIT", "QUIT", "STOP"]:
        return {"approved_path": {"exit": True}}

    selected_path = None
    for path in ranked_paths:
        if str(path.get('path_id')) == selected_id:
            selected_path = path
            break

    if selected_path is None:
        return {"approved_path": {}}

    full_path = all_paths.get(selected_path.get("path_id"), {})

    approved_path = {
        "path_id": selected_path.get("path_id"),
        "rank": selected_path.get("rank"),
        "score": selected_path.get("score"),
        "reason": selected_path.get("reason"),
        "focus": full_path.get("focus", ""),
        "plan": full_path.get("plan", [])
    }
    store.put(("learners",), learner_id, {
        "learner_id": learner_id,
        "known_gaps": state.detected_gaps,
        "approved_path": approved_path,
        "interests": state.learner_profile.interests
    })

    return {
        "approved_path": approved_path
    }


def learning_path_confirmation_gate(state: LearnerState) -> str:
    if not state.approved_path:
        return "learning_path_approval_node"
    elif state.approved_path.get("exit"):
        return "exit"
    else:
        return "approved"


def parent_init_node(state: LearnerState, store: BaseStore) -> Dict[str, Any]:
    learner_id = state.learner_profile.learner

    results = store.search(("learners",), filter={"learner_id": learner_id})
    if results:
        profile = results[0].value
        print(f"📚 Returning learner detected. Loading {len(profile.get('known_gaps', []))} known gaps.")
        return {"known_gaps": profile.get("known_gaps", [])}

    print("👋 New learner detected. Starting fresh.")
    return {}