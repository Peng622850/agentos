import redis
import json
import os
import time
from langchain_openai import ChatOpenAI

r = redis.from_url(os.getenv("REDIS_URL"))

llm = ChatOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("BASE_URL"),
    model=os.getenv("MODEL_NAME"),
)

DEFAULT_PROMPT = "你是任务规划师。用户需求：{user_input}\n请拆解成具体执行步骤。"

def get_current_prompt() -> str:
    prompt = r.get("eval:prompt:current")
    return prompt.decode() if prompt else DEFAULT_PROMPT

def get_prompt_version() -> int:
    v = r.get("eval:prompt:version")
    return int(v) if v else 0

def save_prompt_version(prompt: str, stats: dict):
    version = get_prompt_version() + 1
    r.set("eval:prompt:version", version)
    r.set("eval:prompt:current", prompt)
    r.set(f"eval:prompt:v{version}", json.dumps({
        "prompt": prompt,
        "timestamp": time.time(),
        "stats": stats,
    }, ensure_ascii=False))
    return version

def get_prompt_history() -> list:
    version = get_prompt_version()
    history = []
    for v in range(1, version + 1):
        data = r.get(f"eval:prompt:v{v}")
        if data:
            history.append(json.loads(data))
    return history

async def run_flywheel() -> dict:
    bad_cases_raw = r.lrange("eval:bad_cases", 0, -1)
    if not bad_cases_raw:
        return {"status": "no_bad_cases"}

    bad_cases = [json.loads(i) for i in bad_cases_raw]

    # 按类型统计
    type_counts = {}
    for c in bad_cases:
        t = c.get("error_type", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1

    avg_score = sum(c["score"] for c in bad_cases) / len(bad_cases)

    cases_text = "\n---\n".join([
        f"问题：{c['user_input']}\n回答：{c['result'][:300]}\n评分：{c['score']}\n失败类型：{c.get('error_type','unknown')}\n原因：{c['reason']}"
        for c in bad_cases[:10]
    ])

    current_prompt = get_current_prompt()
    current_version = get_prompt_version()

    response = await llm.ainvoke(f"""你是Prompt优化专家。
当前Planner Prompt（版本v{current_version}）：
{current_prompt}

失败案例分析（共{len(bad_cases)}条，平均分{avg_score:.1f}）：
失败类型分布：{json.dumps(type_counts, ensure_ascii=False)}

具体案例：
{cases_text}

请针对主要失败类型优化Prompt，变量用{{user_input}}占位。
只返回优化后的Prompt文本。""")

    new_prompt = response.content.strip()

    stats = {
        "bad_case_count": len(bad_cases),
        "avg_score": avg_score,
        "type_counts": type_counts,
        "previous_version": current_version,
    }

    new_version = save_prompt_version(new_prompt, stats)

    # 清空已处理的bad case
    r.delete("eval:bad_cases")

    return {
        "status": "optimized",
        "new_version": new_version,
        "bad_case_count": len(bad_cases),
        "avg_score": avg_score,
        "type_counts": type_counts,
        "new_prompt": new_prompt,
    }

async def rollback_prompt(version: int) -> dict:
    data = r.get(f"eval:prompt:v{version}")
    if not data:
        return {"status": "version_not_found"}
    record = json.loads(data)
    r.set("eval:prompt:current", record["prompt"])
    return {"status": "rolled_back", "version": version}