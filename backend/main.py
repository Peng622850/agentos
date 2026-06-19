from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import chat, trace, eval

app = FastAPI(title="AgentOS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")
app.include_router(trace.router, prefix="/api")
app.include_router(eval.router, prefix="/api")

@app.get("/health")
async def health():
    return {"status": "ok"}