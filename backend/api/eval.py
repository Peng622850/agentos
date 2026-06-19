from fastapi import APIRouter
from pydantic import BaseModel
from eval.judge import Judge

router = APIRouter()

class EvalRequest(BaseModel):
    session_id: str
    question: str
    answer: str

@router.post("/eval")
async def run_eval(req: EvalRequest):
    judge = Judge()
    result = await judge.score(req.question, req.answer)
    return result