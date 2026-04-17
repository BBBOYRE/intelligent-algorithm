from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

from server.auth.security import get_current_user
from server.models.user import User
from server.database import get_db
from server.dependencies import get_kb
from server.models.chat import ChatSession, ChatMessage

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []
    kb_id: str = "default"
    team_id: Optional[str] = None
    session_id: Optional[str] = None

class ChatMessageModel(BaseModel):
    id: str
    role: str
    content: str
    created_at: str

class ChatSessionModel(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    messages: List[ChatMessageModel] = []

class SessionUpdate(BaseModel):
    title: str

class ChatResponse(BaseModel):
    reply: str
    session_id: Optional[str] = None


@router.get("/chat/sessions")
def get_sessions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sessions = db.query(ChatSession).filter(ChatSession.user_id == current_user.id).order_by(ChatSession.updated_at.desc()).all()
    result = []
    for s in sessions:
        msgs = db.query(ChatMessage).filter(ChatMessage.session_id == s.id).order_by(ChatMessage.created_at.asc()).all()
        result.append({
            "id": s.id,
            "title": s.title,
            "created_at": s.created_at.isoformat() + "Z" if s.created_at else "",
            "updated_at": s.updated_at.isoformat() + "Z" if s.updated_at else "",
            "messages": [{"id": m.id, "role": m.role, "content": m.content, "created_at": m.created_at.isoformat() + "Z"} for m in msgs]
        })
    return result

@router.post("/chat/sessions")
def create_session(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_session = ChatSession(id=f"chat_{uuid.uuid4().hex[:8]}", user_id=current_user.id)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return {
        "id": new_session.id,
        "title": new_session.title,
        "created_at": new_session.created_at.isoformat() + "Z",
        "updated_at": new_session.updated_at.isoformat() + "Z",
        "messages": []
    }

@router.patch("/chat/sessions/{session_id}")
def update_session(session_id: str, update: SessionUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session.title = update.title
    db.commit()
    return {"status": "success"}

@router.delete("/chat/sessions/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()
    return {"status": "success"}


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from core.agent import DocumentAgent
    
    # Ensure session exists
    session_id = req.session_id
    if session_id:
        session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
        if not session:
            session = ChatSession(id=session_id, user_id=current_user.id)
            db.add(session)
            db.commit()
    else:
        session = ChatSession(id=f"chat_{uuid.uuid4().hex[:8]}", user_id=current_user.id)
        db.add(session)
        db.commit()
        session_id = session.id

    # Insert user message
    user_msg = ChatMessage(
        id=f"msg_{uuid.uuid4().hex[:8]}",
        session_id=session_id,
        role="user",
        content=req.message
    )
    db.add(user_msg)
    
    try:
        kb = get_kb(current_user.id, req.kb_id, team_id=req.team_id)
        agent = DocumentAgent(kb)
        answer = agent.chat(req.message, req.history)
    except Exception as exc:
        answer = f"对话请求失败: {exc}"

    # Insert assistant message
    asst_msg = ChatMessage(
        id=f"msg_{uuid.uuid4().hex[:8]}",
        session_id=session_id,
        role="assistant",
        content=answer
    )
    db.add(asst_msg)
    
    session.updated_at = datetime.utcnow()
    db.commit()

    return ChatResponse(reply=answer, session_id=session_id)
