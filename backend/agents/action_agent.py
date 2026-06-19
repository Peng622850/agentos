from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from agents.state import AgentState
from tools.web_search import web_search
from tools.file_tool import read_file, write_file
from tools.shell_tool import run_shell
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

    # 处理工具调用
    if response.tool_calls:
        for tc in response.tool_calls:
            if tc["name"] == "search":
                result = await web_search(tc["args"]["query"])
                state["result"] = result
                return state

    state["result"] = response.content
    return state