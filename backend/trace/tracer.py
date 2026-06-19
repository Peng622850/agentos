import redis
import json
import os
import time

r = redis.from_url(os.getenv("REDIS_URL"))

class Tracer:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.key = f"trace:{session_id}"

    def log(self, node: str, data: dict):
        span = {
            "node": node,
            "timestamp": time.time(),
            "data": data,
        }
        r.lpush(self.key, json.dumps(span, ensure_ascii=False))
        r.expire(self.key, 86400)  # 保留1天

    def get_trace(self) -> list:
        items = r.lrange(self.key, 0, -1)
        return [json.loads(i) for i in items]