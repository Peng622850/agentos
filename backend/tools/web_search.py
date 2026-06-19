import httpx
import os
from tools.registry import register

@register("web_search")
async def web_search(query: str) -> str:
    """搜索网页，返回摘要结果"""
    api_key = os.getenv("TAVILY_API_KEY")
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.tavily.com/search",
            json={"api_key": api_key, "query": query, "max_results": 3}
        )
        data = resp.json()
        results = data.get("results", [])
        return "\n".join([f"{r['title']}: {r['content'][:200]}" for r in results])