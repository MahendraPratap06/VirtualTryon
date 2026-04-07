from langgraph.graph import StateGraph, END

from src.langchainagenticai.state.state import TryOnState
from src.langchainagenticai.nodes.validate_images import validate_images
from src.langchainagenticai.nodes.preprocess_images import preprocess_images
from src.langchainagenticai.nodes.virtual_tryon import virtual_tryon
from src.langchainagenticai.nodes.display_result import display_result


def should_stop(state: TryOnState) -> str:
    """
    Conditional edge — called after every node.
    If any node sets status="error", route to END immediately.
    Otherwise continue to next node.
    """
    if state["status"] == "error":
        return "stop"
    return "continue"


def build_graph() -> StateGraph:
    """
    Builds and compiles the LangGraph pipeline.

    Flow:
    validate_images → preprocess_images → virtual_tryon → display_result → END

    At each step, if status="error" the graph stops early via conditional edge.
    """

    graph = StateGraph(TryOnState)

   
    graph.add_node("validate_images",    validate_images)
    graph.add_node("preprocess_images",  preprocess_images)
    graph.add_node("virtual_tryon",      virtual_tryon)
    graph.add_node("display_result",     display_result)

    
    graph.set_entry_point("validate_images")


    graph.add_conditional_edges(
        "validate_images",
        should_stop,
        {"stop": END, "continue": "preprocess_images"}
    )

    graph.add_conditional_edges(
        "preprocess_images",
        should_stop,
        {"stop": END, "continue": "virtual_tryon"}
    )

    graph.add_conditional_edges(
        "virtual_tryon",
        should_stop,
        {"stop": END, "continue": "display_result"}
    )

    graph.add_edge("display_result", END)

    return graph.compile()