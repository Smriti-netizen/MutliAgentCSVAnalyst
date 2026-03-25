import json

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from agents.state import AnalystState

SYSTEM_PROMPT = """You are a strict fact-checker for data analysis reports.

Your job:
1. Compare EVERY numerical claim in the report against the code output.
2. If any number is fabricated, rounded incorrectly, or misinterpreted — reject the report.
3. If the report omits important findings from the code output — reject the report.
4. If everything checks out — approve the report.

Respond with ONLY a JSON object (no markdown fences, no extra text):
{
    "review_passed": true or false,
    "review_feedback": "explanation of issues found, or 'All claims verified.' if approved"
}"""


def _parse_review(text: str) -> tuple[bool, str]:
    """Extract review_passed and review_feedback from the LLM response."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

    try:
        data = json.loads(cleaned)
        return bool(data.get("review_passed", False)), str(data.get("review_feedback", ""))
    except (json.JSONDecodeError, AttributeError):
        return False, f"Could not parse reviewer response: {text[:200]}"


def reviewer_node(state: AnalystState) -> dict:
    """LangGraph node: validates that the report matches the code output."""
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

    user_content = (
        f"## Code Output (ground truth)\n{state.get('code_output', '')}\n\n"
        f"## Report to Review\n{state.get('report', '')}"
    )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]

    response = llm.invoke(messages)
    passed, feedback = _parse_review(response.content)

    return {
        "review_passed": passed,
        "review_feedback": feedback,
        "retry_count": state.get("retry_count", 0) + (0 if passed else 1),
    }
