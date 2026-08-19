from nodes import (parent_init_node, evaluation_node, gap_confirmation_node, candidate_path_node,
                   learning_path_approval_node, check_gap_confirmation_gate, learning_path_confirmation_gate,
                   learning_path_worker,QuestionGeneratorNode,follow_up_node,summarisation_node)
from langgraph.graph import StateGraph, START, END
from graph_states import LearnerState, LearningPathWorkerState,InterviewSubgraphState
from storage import store, db_checkpointer



#########

interview_builder = StateGraph(InterviewSubgraphState)

# Register Subgraph Nodes
interview_builder.add_node("question_generator", QuestionGeneratorNode)
interview_builder.add_node("follow_up", follow_up_node)
interview_builder.add_node("summarisation", summarisation_node)

# Linear flow inside the subgraph
interview_builder.add_edge(START, "question_generator")  # Subgraph starts at question generator
interview_builder.add_edge("question_generator", "follow_up")


def check_approval_status(state: InterviewSubgraphState) -> str:
    """Pure routing conditional check based on state attributes."""
    if state.subgraph_approval == "approved":
        return "finish"
    return "loop_back"


# FIX: Origin node must be "follow_up"
interview_builder.add_conditional_edges(
    "follow_up",
    check_approval_status,
    {
        "finish": "summarisation",
        "loop_back": "question_generator"
    }
)
interview_builder.add_edge("summarisation", END)  # Subgraph MUST end at END

# Compile the Subgraph independently

compiled_interview_subgraph = interview_builder.compile()


####

worker_builder = StateGraph(LearningPathWorkerState)
worker_builder.add_node("learning_path_worker", learning_path_worker)
worker_builder.add_edge(START, "learning_path_worker")
worker_builder.add_edge("learning_path_worker", END)
compiled_worker = worker_builder.compile()


########


parent_builder = StateGraph(LearnerState)

# 1. Register Parent Nodes
parent_builder.add_node("parent_init", parent_init_node)
parent_builder.add_node("interview_loop", compiled_interview_subgraph)
parent_builder.add_node("evaluation_node", evaluation_node)
parent_builder.add_node("gap_confirmation_node", gap_confirmation_node)
parent_builder.add_node("learning_path_worker", compiled_worker)
parent_builder.add_node("candidate_path_node", candidate_path_node)
parent_builder.add_node("learning_path_approval_node", learning_path_approval_node)

# 2. Wire the Parent Graph Path
parent_builder.add_edge(START, "parent_init")
parent_builder.add_edge("parent_init", "interview_loop")
parent_builder.add_edge("interview_loop", "evaluation_node")
parent_builder.add_edge("evaluation_node", "gap_confirmation_node")
parent_builder.add_edge("learning_path_worker", "candidate_path_node")
parent_builder.add_edge("candidate_path_node", "learning_path_approval_node")

parent_builder.add_conditional_edges(
    "gap_confirmation_node",
    check_gap_confirmation_gate,
    {
        "interview_loop": "interview_loop",
        "gap_confirmation_node": "gap_confirmation_node"
    }
)

parent_builder.add_conditional_edges(
    "learning_path_approval_node",
    learning_path_confirmation_gate,
    {
        "approved": END,
        "exit": END,
        "learning_path_approval_node": "learning_path_approval_node"
    }
)

#parent_graph = parent_builder.compile(checkpointer=db_checkpointer, store=store)

parent_graph = parent_builder.compile()
graph = parent_graph
