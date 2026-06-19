from langchain_openai import ChatOpenAI
from agents.state import AgentState
import os

llm = ChatOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("BASE_URL"),
    model=os.getenv("MODEL_NAME"),
)

async def critic_node(state: AgentState) -> AgentState:
    prompt = f"""你是质量评审员。
用户问题：{state['user_input']}
执行结果：{state['result']}
请从1-5分打分，只返回JSON：{{"score": 4.2, "reason": "..."}}"""
    response = await llm.ainvoke(prompt)
    import json
    try:
        data = json.loads(response.content)
        state["score"] = data.get("score", 0.0)
    except:
        state["score"] = 0.0
    return state