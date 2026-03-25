from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from agents.state import AnalystState

SYSTEM_PROMPT = """You are a professional data analyst writing a report for a non-technical audience.

Rules:
1. Write a clear, well-structured Markdown report that answers the user's question.
2. Use headers (##), bullet points, and bold text for readability.
3. Every number you mention MUST come directly from the code output provided. Do NOT invent or estimate numbers.
4. Explain what the numbers mean in plain English. Add business context where appropriate.
5. If the code output is empty or unclear, say so honestly rather than making up results.
6. Keep the report concise — aim for 150-300 words."""


def analyst_node(state: AnalystState) -> dict:
    """LangGraph node: writes a Markdown report from the code output."""
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)

    user_content = (
        f"## User's Question\n{state['user_question']}\n\n"
        f"## Code Output (ground truth)\n{state.get('code_output', 'No output available.')}"
    )

    if state.get("review_feedback"):
        user_content += (
            f"\n\n## Reviewer Feedback (fix these issues)\n{state['review_feedback']}"
        )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]

    response = llm.invoke(messages)

    return {"report": response.content}
