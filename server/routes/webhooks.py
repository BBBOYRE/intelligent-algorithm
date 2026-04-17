import secrets
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from server.database import get_db
from server.auth.security import get_current_user
from server.models.user import User
from server.models.webhook import Webhook

router = APIRouter()


class WebhookCreate(BaseModel):
    url: str
    events: str = ""


@router.post("/webhooks", status_code=201)
async def create_webhook(
    data: WebhookCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not data.url.strip():
        raise HTTPException(status_code=400, detail="URL 不能为空")
    secret = secrets.token_hex(16)
    hook = Webhook(
        user_id=current_user.id,
        url=data.url.strip(),
        events=data.events,
        secret=secret,
    )
    db.add(hook)
    db.commit()
    db.refresh(hook)
    return {
        "id": hook.id,
        "url": hook.url,
        "events": hook.events,
        "secret": secret,
        "created_at": hook.created_at.isoformat(),
    }


@router.get("/webhooks")
async def list_webhooks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    hooks = db.query(Webhook).filter(
        Webhook.user_id == current_user.id
    ).order_by(Webhook.created_at.desc()).all()
    return [
        {
            "id": h.id,
            "url": h.url,
            "events": h.events,
            "is_active": h.is_active,
            "created_at": h.created_at.isoformat(),
        }
        for h in hooks
    ]


@router.delete("/webhooks/{webhook_id}", status_code=204)
async def delete_webhook(
    webhook_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    hook = db.query(Webhook).filter(
        Webhook.id == webhook_id, Webhook.user_id == current_user.id
    ).first()
    if not hook:
        raise HTTPException(status_code=404, detail="Webhook 不存在")
    db.delete(hook)
    db.commit()
