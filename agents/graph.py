from typing import Literal

from langgraph.graph import END, START, StateGraph

from agents.analyst import analyst_node
from agents.coder import coder_node
from agents.executor import executor_node
from agents.reviewer import reviewer_node
from agents.state import AnalystState
from utils.data_profiler import profile_all_datasets

MAX_RETRIES = 3


def profiler_node(state: AnalystState) -> dict:
    """LangGraph node: extracts schema and sample rows from all CSVs."""
    paths = state.get("all_df_paths") or [state["df_path"]]
    dataset_info = profile_all_datasets(paths)
    return {"dataset_info": dataset_info}


def route_after_execution(state: AnalystState) -> Literal["coder", "analyst"]:
    """If code failed and retries remain, loop back to coder. Else continue."""
    if state.get("code_error") and state.get("retry_count", 0) < MAX_RETRIES:
        return "coder"
    return "analyst"


def route_after_review(state: AnalystState) -> Literal["analyst", "__end__"]:
    """If review failed and retries remain, loop back to analyst. Else finish."""
    if not state.get("review_passed") and state.get("retry_count", 0) < MAX_RETRIES:
        return "analyst"
    return END


def build_graph():
    """Construct and compile the multi-agent analysis graph."""
    graph = StateGraph(AnalystState)

    graph.add_node("profiler", profiler_node)
    graph.add_node("coder", coder_node)
    graph.add_node("executor", executor_node)
    graph.add_node("analyst", analyst_node)
    graph.add_node("reviewer", reviewer_node)

    graph.add_edge(START, "profiler")
    graph.add_edge("profiler", "coder")
    graph.add_edge("coder", "executor")
    graph.add_conditional_edges("executor", route_after_execution)
    graph.add_edge("analyst", "reviewer")
    graph.add_conditional_edges("reviewer", route_after_review)

    return graph.compile()
