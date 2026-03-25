from agents.state import AnalystState
from utils.sandbox import run_sandboxed


def executor_node(state: AnalystState) -> dict:
    """LangGraph node: runs the generated code in a sandboxed environment."""
    output, error = run_sandboxed(state["generated_code"], state["df_path"])

    if error:
        return {
            "code_error": error,
            "code_output": "",
            "retry_count": state.get("retry_count", 0) + 1,
        }

    return {
        "code_output": output,
        "code_error": "",
    }
