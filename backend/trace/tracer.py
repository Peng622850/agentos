import redis
import json
import os
import time

r = redis.from_url(os.getenv("REDIS_URL"))

class Tracer:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.key = f"trace:{session_id}"
        self.run_id = str(time.time())

    def start_span(self, node: str) -> float:
        return time.time()

    def end_span(self, node: str, start_time: float, input_text: str, output_text: str, tokens: int = 0):
        span = {
            "run_id": self.run_id,
            "node": node,
            "start_time": start_time,
            "end_time": time.time(),
            "latency_ms": round((time.time() - start_time) * 1000),
            "input": input_text[:300],
            "output": output_text[:300],
            "tokens": tokens,
        }
        r.lpush(self.key, json.dumps(span, ensure_ascii=False))
        r.expire(self.key, 86400)

    def get_trace(self) -> list:
        items = r.lrange(self.key, 0, -1)
        return [json.loads(i) for i in items]