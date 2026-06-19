from langchain_openai import ChatOpenAI
from agents.state import AgentState
import os
import json
import re
import redis
import time

r = redis.from_url(os.getenv("REDIS_URL"))

llm = ChatOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("BASE_URL"),
    model=os.getenv("MODEL_NAME"),
)


async def critic_node(state: AgentState) -> AgentState:
    prompt = f"""你是严格的质量评审员，只返回JSON，不要有任何其他内容。
    用户问题：{state['user_input']}
    执行结果：{state['result']}

    评分标准（严格执行）：
    - 5分：完美回答，直接解决用户问题
    - 4分：基本解决，有少量不足
    - 3分：部分解决，存在明显缺陷
    - 2分：未能解决问题，回答偏离主题
    - 1分：用户输入无意义或回答完全错误

    如果用户输入是随机字符、数字、乱码等无意义内容，最高给2分。
    如果回答没有直接解决用户的实际需求，最高给3分。

    返回格式：{{"score": 2.0, "reason": "简短理由", "error_type": "none"}}
    error_type: none / planning_error / tool_error / quality_error"""

    response = await llm.ainvoke(prompt)
    content = response.content.strip()

    match = re.search(r'\{.*?\}', content, re.DOTALL)
    score = 0.0
    reason = ""
    error_type = "none"

    if match:
        try:
            data = json.loads(match.group())
            score = float(data.get("score", 0.0))
            reason = data.get("reason", "")
            error_type = data.get("error_type", "none")
        except:
            pass

    state["score"] = score
    state["error_type"] = error_type

    if score < 3.0:
        bad_case = {
            "timestamp": time.time(),
            "session_id": state["session_id"],
            "user_input": state["user_input"],
            "result": state["result"],
            "score": score,
            "reason": reason,
            "error_type": error_type,
        }
        r.lpush("eval:bad_cases", json.dumps(bad_case, ensure_ascii=False))

        # 按类型分别存储
        r.lpush(f"eval:bad_cases:{error_type}", json.dumps(bad_case, ensure_ascii=False))

        # 自动触发飞轮（积累10条）
        count = r.llen("eval:bad_cases")
        if count >= 10:
            from eval.flywheel import run_flywheel
            import asyncio
            asyncio.create_task(run_flywheel())

    return state