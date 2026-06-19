from fastapi import APIRouter
from trace.tracer import Tracer

router = APIRouter()

@router.get("/trace/{session_id}")
async def get_trace(session_id: str):
    tracer = Tracer(session_id)
    return {"trace": tracer.get_trace()}