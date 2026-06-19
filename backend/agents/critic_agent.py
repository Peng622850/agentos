from langchain_openai import ChatOpenAI
from agents.state import AgentState
import os
import json
import re

llm = ChatOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("BASE_URL"),
    model=os.getenv("MODEL_NAME"),
)


async def critic_node(state: AgentState) -> AgentState:
    prompt = f"""你是质量评审员，只返回JSON，不要有任何其他内容。
用户问题：{state['user_input']}
执行结果：{state['result']}
返回格式：{{"score": 4.2, "reason": "简短理由"}}"""

    response = await llm.ainvoke(prompt)
    content = response.content.strip()

    # 提取JSON，兼容模型返回markdown代码块的情况
    match = re.search(r'\{.*?\}', content, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group())
            state["score"] = float(data.get("score", 0.0))
        except:
            state["score"] = 0.0
    else:
        state["score"] = 0.0

    return state