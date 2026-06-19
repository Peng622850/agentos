from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from agents.supervisor import Supervisor

router = APIRouter()

class ChatRequest(BaseModel):
    session_id: str
    message: str

@router.post("/chat")
async def chat(req: ChatRequest):
    supervisor = Supervisor(req.session_id)
    return StreamingResponse(
        supervisor.run(req.message),
        media_type="text/event-stream"
    )