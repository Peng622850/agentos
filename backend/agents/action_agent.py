from langchain_openai import ChatOpenAI
from agents.state import AgentState
import os

llm = ChatOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("BASE_URL"),
    model=os.getenv("MODEL_NAME"),
)

async def action_node(state: AgentState) -> AgentState:
    prompt = f"你是执行专家。根据以下计划生成最终回答：\n{state['plan']}"
    response = await llm.ainvoke(prompt)
    state["result"] = response.content
    return state