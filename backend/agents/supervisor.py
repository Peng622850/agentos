import json
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from typing import AsyncGenerator
from agents.state import AgentState
from agents.planner_agent import planner_node
from agents.action_agent import action_node
from agents.critic_agent import critic_node
from memory.session import SessionMemory
from trace.tracer import Tracer
import os

llm = ChatOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("BASE_URL"),
    model=os.getenv("MODEL_NAME"),
)

def build_graph():
    g = StateGraph(AgentState)
    g.add_node("planner", planner_node)
    g.add_node("action", action_node)
    g.add_node("critic", critic_node)
    g.set_entry_point("planner")
    g.add_edge("planner", "action")
    g.add_edge("action", "critic")
    g.add_edge("critic", END)
    return g.compile()

graph = build_graph()

class Supervisor:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.memory = SessionMemory(session_id)
        self.tracer = Tracer(session_id)

    async def run(self, user_input: str) -> AsyncGenerator:
        state = {
            "session_id": self.session_id,
            "user_input": user_input,
            "plan": "",
            "result": "",
            "score": 0.0,
            "error_type": "none",
            "messages": self.memory.get_history(),
            "tracer": self.tracer,
        }
        async for event in graph.astream(state):
            # 序列化前去掉tracer对象
            serializable = {}
            for node_name, node_state in event.items():
                clean = {k: v for k, v in node_state.items() if k != "tracer"}
                serializable[node_name] = clean
            chunk = json.dumps(serializable, ensure_ascii=False)
            yield f"data: {chunk}\n\n"
        self.memory.save(user_input, state.get("result", ""))