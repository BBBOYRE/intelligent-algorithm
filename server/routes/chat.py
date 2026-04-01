from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []

class ChatResponse(BaseModel):
    reply: str

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    from core.agent import DocumentAgent
    from core.knowledge_base import KnowledgeBase
    try:
        agent = DocumentAgent(KnowledgeBase())
        answer = agent.chat(req.message, req.history)
        return ChatResponse(reply=answer)
    except Exception as exc:
        return ChatResponse(reply=f"对话请求失败: {exc}")
