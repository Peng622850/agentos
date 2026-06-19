from langchain_openai import ChatOpenAI
import json
import os

llm = ChatOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("BASE_URL"),
    model=os.getenv("MODEL_NAME"),
)

class Judge:
    async def score(self, question: str, answer: str) -> dict:
        prompt = f"""你是专业评测员，对AI回答打分。
问题：{question}
回答：{answer}
只返回JSON：{{"relevancy": 4.5, "faithfulness": 4.0, "completeness": 3.8, "reason": "..."}}"""
        response = await llm.ainvoke(prompt)
        try:
            return json.loads(response.content)
        except:
            return {"relevancy": 0, "faithfulness": 0, "completeness": 0, "reason": "解析失败"}