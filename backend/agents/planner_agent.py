from langchain_openai import ChatOpenAI
from agents.state import AgentState
import os

llm = ChatOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("BASE_URL"),
    model=os.getenv("MODEL_NAME"),
)

async def planner_node(state: AgentState) -> AgentState:
    prompt = f"你是任务规划师。用户需求：{state['user_input']}\n请拆解成具体执行步骤。"
    response = await llm.ainvoke(prompt)
    state["plan"] = response.content
    return state