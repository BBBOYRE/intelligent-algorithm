from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

from server.auth.security import get_current_user
from server.models.user import User
from server.dependencies import get_kb

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []
    kb_id: str = "default"
    team_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    from core.agent import DocumentAgent
    try:
        kb = get_kb(current_user.id, req.kb_id, team_id=req.team_id)
        agent = DocumentAgent(kb)
        answer = agent.chat(req.message, req.history)
        return ChatResponse(reply=answer)
    except Exception as exc:
        return ChatResponse(reply=f"对话请求失败: {exc}")
