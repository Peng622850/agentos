from fastapi import APIRouter
from pydantic import BaseModel
from eval.judge import Judge
from eval.flywheel import run_flywheel, get_prompt_history, rollback_prompt, get_current_prompt
import redis
import json
import os

r = redis.from_url(os.getenv("REDIS_URL"))
router = APIRouter()

class EvalRequest(BaseModel):
    session_id: str
    question: str
    answer: str

class RollbackRequest(BaseModel):
    version: int

@router.post("/eval")
async def run_eval(req: EvalRequest):
    judge = Judge()
    return await judge.score(req.question, req.answer)

@router.post("/eval/flywheel")
async def trigger_flywheel():
    return await run_flywheel()

@router.get("/eval/bad_cases")
async def get_bad_cases():
    items = r.lrange("eval:bad_cases", 0, -1)
    return {"bad_cases": [json.loads(i) for i in items], "count": len(items)}

@router.get("/eval/prompt_history")
async def get_history():
    return {"history": get_prompt_history(), "current_prompt": get_current_prompt()}

@router.post("/eval/rollback")
async def rollback(req: RollbackRequest):
    return await rollback_prompt(req.version)