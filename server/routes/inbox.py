from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

from server.auth.security import get_current_user
from server.models.user import User
from server.models.inbox import InboxMessage
from server.database import get_db

router = APIRouter()


class SendMessageRequest(BaseModel):
    recipient_email: str
    title: str
    content: str = ""


@router.get("/inbox")
def get_inbox(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    msgs = db.query(InboxMessage).filter(
        InboxMessage.recipient_id == current_user.id
    ).order_by(InboxMessage.created_at.desc()).all()
    result = []
    for m in msgs:
        sender = db.query(User).filter(User.id == m.sender_id).first()
        result.append({
            "id": m.id,
            "sender_id": m.sender_id,
            "sender_name": sender.username if sender else "unknown",
            "type": m.type,
            "title": m.title,
            "content": m.content,
            "team_id": m.team_id,
            "status": m.status,
            "created_at": m.created_at.isoformat() + "Z" if m.created_at else "",
        })
    return result


@router.get("/inbox/unread-count")
def unread_count(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    count = db.query(InboxMessage).filter(
        InboxMessage.recipient_id == current_user.id,
        InboxMessage.status == "unread"
    ).count()
    return {"count": count}


@router.patch("/inbox/{msg_id}/read")
def mark_read(msg_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    msg = db.query(InboxMessage).filter(InboxMessage.id == msg_id, InboxMessage.recipient_id == current_user.id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    if msg.status == "unread":
        msg.status = "read"
        db.commit()
    return {"status": "success"}


@router.post("/inbox/{msg_id}/accept")
def accept_invite(msg_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    msg = db.query(InboxMessage).filter(InboxMessage.id == msg_id, InboxMessage.recipient_id == current_user.id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    if msg.type != "team_invite":
        raise HTTPException(status_code=400, detail="Not an invitation")
    if msg.status in ("accepted", "rejected"):
        raise HTTPException(status_code=400, detail="Already processed")
    from server.models.team import Team, TeamMember
    team = db.query(Team).filter(Team.id == msg.team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team no longer exists")
    existing = db.query(TeamMember).filter(TeamMember.team_id == msg.team_id, TeamMember.user_id == current_user.id).first()
    if not existing:
        member = TeamMember(team_id=msg.team_id, user_id=current_user.id, role="member")
        db.add(member)
    msg.status = "accepted"
    db.commit()
    return {"status": "accepted"}


@router.post("/inbox/{msg_id}/reject")
def reject_invite(msg_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    msg = db.query(InboxMessage).filter(InboxMessage.id == msg_id, InboxMessage.recipient_id == current_user.id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    if msg.type != "team_invite":
        raise HTTPException(status_code=400, detail="Not an invitation")
    msg.status = "rejected"
    db.commit()
    return {"status": "rejected"}


@router.post("/inbox/send")
def send_message(req: SendMessageRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    recipient = db.query(User).filter(User.email == req.recipient_email).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    if recipient.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot send to yourself")
    msg = InboxMessage(
        recipient_id=recipient.id,
        sender_id=current_user.id,
        type="message",
        title=req.title,
        content=req.content,
    )
    db.add(msg)
    db.commit()
    return {"status": "sent"}


@router.delete("/inbox/{msg_id}")
def delete_message(msg_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    msg = db.query(InboxMessage).filter(InboxMessage.id == msg_id, InboxMessage.recipient_id == current_user.id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    db.delete(msg)
    db.commit()
    return {"status": "deleted"}
