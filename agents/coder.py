import re

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from agents.state import AnalystState

SYSTEM_PROMPT = """You are an expert Python data analyst. Given a dataset description and a user question, write Pandas code that answers the question.

Rules you MUST follow:
1. The primary DataFrame is already loaded as `df`. Do NOT call pd.read_csv or read any files.
2. If multiple datasets are provided, they are available as `df1`, `df2`, `df3`, etc. in addition to `df` (which equals `df1`).
3. `pd` (pandas) and `np` (numpy) are already imported. Do NOT import anything.
4. Print ALL results using print(). The output must fully answer the question.
5. Do NOT create plots or visualizations. Only compute and print.
6. Do NOT use display(), show(), or any Jupyter-specific functions.
7. Write clean, efficient code. Use descriptive variable names.
8. Return ONLY the Python code. No explanations, no markdown fences."""

_FENCE_RE = re.compile(r"^```(?:python)?\s*\n?(.*?)\n?```$", re.DOTALL)


def _strip_fences(text: str) -> str:
    """Remove markdown code fences that LLMs often wrap code in."""
    match = _FENCE_RE.search(text.strip())
    return match.group(1).strip() if match else text.strip()


def coder_node(state: AnalystState) -> dict:
    """LangGraph node: generates Pandas code from the user question."""
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

    user_content = f"## Dataset Info\n{state['dataset_info']}\n\n## Question\n{state['user_question']}"

    if state.get("code_error"):
        user_content += (
            f"\n\n## Previous Code (FAILED)\n```python\n{state['generated_code']}\n```"
            f"\n\n## Error\n{state['code_error']}"
            f"\n\nFix the code to avoid this error."
        )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]

    response = llm.invoke(messages)
    code = _strip_fences(response.content)

    return {"generated_code": code}
