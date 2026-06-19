import redis
import json
import os

r = redis.from_url(os.getenv("REDIS_URL"))

class SessionMemory:
    def __init__(self, session_id: str):
        self.key = f"session:{session_id}"

    def get_history(self) -> list:
        data = r.get(self.key)
        return json.loads(data) if data else []

    def save(self, user_input: str, result: str):
        history = self.get_history()
        history.append({"user": user_input, "assistant": result})
        history = history[-10:]  # 只保留最近10条
        r.setex(self.key, 3600, json.dumps(history, ensure_ascii=False))