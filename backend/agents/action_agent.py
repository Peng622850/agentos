from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from agents.state import AgentState
from tools.web_search import web_search
import os

llm = ChatOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("BASE_URL"),
    model=os.getenv("MODEL_NAME"),
)

@tool
async def search(query: str) -> str:
    """搜索网页获取最新信息"""
    return await web_search(query)

tools = [search]
llm_with_tools = llm.bind_tools(tools)

async def action_node(state: AgentState) -> AgentState:
    response = await llm_with_tools.ainvoke(
        f"用户需求：{state['user_input']}\n计划：{state['plan']}\n请完成任务，需要搜索时使用search工具。"
    )

    if response.tool_calls:
        for tc in response.tool_calls:
            if tc["name"] == "search":
                raw = await web_search(tc["args"]["query"])
                # 让LLM基于搜索结果用中文整理回答
                summary = await llm.ainvoke(
                    f"根据以下搜索结果，用中文详细回答用户问题：{state['user_input']}\n\n搜索结果：{raw}"
                )
                state["result"] = summary.content
                return state

    state["result"] = response.content
    return state