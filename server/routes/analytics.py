from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date

from server.database import get_db
from server.auth.security import get_current_user
from server.models.user import User
from server.models.audit_log import AuditLog

router = APIRouter()


@router.get("/analytics/overview")
async def get_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    uid = current_user.id
    total_uploads = db.query(func.count(AuditLog.id)).filter(AuditLog.user_id == uid, AuditLog.action == "upload").scalar() or 0
    total_chats = db.query(func.count(AuditLog.id)).filter(AuditLog.user_id == uid, AuditLog.action == "chat").scalar() or 0
    total_fills = db.query(func.count(AuditLog.id)).filter(AuditLog.user_id == uid, AuditLog.action == "table_fill").scalar() or 0
    total_doc_ops = db.query(func.count(AuditLog.id)).filter(AuditLog.user_id == uid, AuditLog.action == "doc_ops").scalar() or 0
    avg_fill_time = db.query(func.avg(AuditLog.duration_ms)).filter(AuditLog.user_id == uid, AuditLog.action == "table_fill").scalar() or 0

    return {
        "total_uploads": total_uploads,
        "total_chats": total_chats,
        "total_fills": total_fills,
        "total_doc_ops": total_doc_ops,
        "avg_fill_time_ms": round(avg_fill_time),
    }


@router.get("/analytics/usage")
async def get_usage_trend(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """按天聚合最近 N 天的操作次数"""
    uid = current_user.id
    rows = (
        db.query(
            cast(AuditLog.created_at, Date).label("date"),
            AuditLog.action,
            func.count(AuditLog.id).label("count"),
        )
        .filter(AuditLog.user_id == uid)
        .group_by(cast(AuditLog.created_at, Date), AuditLog.action)
        .order_by(cast(AuditLog.created_at, Date))
        .all()
    )

    trend = {}
    for row in rows:
        date_str = str(row.date)
        if date_str not in trend:
            trend[date_str] = {}
        trend[date_str][row.action] = row.count

    return {"trend": trend}
