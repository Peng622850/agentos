from langchain_openai import ChatOpenAI
from agents.state import AgentState
from eval.flywheel import get_current_prompt
import os

llm = ChatOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("BASE_URL"),
    model=os.getenv("MODEL_NAME"),
)

async def planner_node(state: AgentState) -> AgentState:
    tracer = state.get("tracer")
    start = tracer.start_span("planner") if tracer else None

    prompt_template = get_current_prompt()
    prompt = prompt_template.format(user_input=state['user_input'])
    response = await llm.ainvoke(prompt)
    state["plan"] = response.content

    if tracer and start:
        tracer.end_span("planner", start, prompt, state["plan"])

    return state