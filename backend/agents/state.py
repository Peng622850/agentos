from typing import TypedDict

class AgentState(TypedDict):
    session_id: str
    user_input: str
    plan: str
    result: str
    score: float
    messages: list