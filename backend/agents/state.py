from typing import TypedDict

class AgentState(TypedDict):
    session_id: str
    user_input: str
    plan: str
    result: str
    score: float
    error_type: str
    messages: list