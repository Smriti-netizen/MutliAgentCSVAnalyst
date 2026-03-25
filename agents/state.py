from typing import TypedDict


class AnalystState(TypedDict, total=False):
    user_question: str
    dataset_info: str
    df_path: str
    generated_code: str
    code_output: str
    code_error: str
    report: str
    review_passed: bool
    review_feedback: str
    retry_count: int
    messages: list
