"""异步 Webhook 事件分发器"""
import hashlib
import hmac
import json
import logging
from datetime import datetime, timezone

import httpx
from sqlalchemy.orm import Session

from server.database import SessionLocal
from server.models.webhook import Webhook

logger = logging.getLogger(__name__)

VALID_EVENTS = {"document.uploaded", "document.batch_done", "table.filled", "team.member_added"}


async def dispatch_event(user_id: str, event: str, payload: dict):
    db: Session = SessionLocal()
    try:
        hooks = db.query(Webhook).filter(
            Webhook.user_id == user_id,
            Webhook.is_active == True,
        ).all()

        for hook in hooks:
            subscribed = [e.strip() for e in hook.events.split(",") if e.strip()]
            if subscribed and event not in subscribed:
                continue
            await _send(hook, event, payload)
    except Exception as e:
        logger.error(f"webhook dispatch error: {e}")
    finally:
        db.close()


async def _send(hook: Webhook, event: str, payload: dict):
    body = json.dumps({"event": event, "timestamp": datetime.now(timezone.utc).isoformat(), "data": payload}, ensure_ascii=False)
    headers = {"Content-Type": "application/json", "X-Webhook-Event": event}
    if hook.secret:
        sig = hmac.new(hook.secret.encode(), body.encode(), hashlib.sha256).hexdigest()
        headers["X-Webhook-Signature"] = sig
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(hook.url, content=body, headers=headers)
    except Exception as e:
        logger.warning(f"webhook send failed to {hook.url}: {e}")
