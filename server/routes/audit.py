from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from server.database import get_db
from server.auth.security import get_current_user
from server.models.user import User
from server.models.audit_log import AuditLog

router = APIRouter()


@router.get("/audit/logs")
async def get_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    action: str = Query(""),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(AuditLog)

    # 非管理员只能看自己的日志
    if current_user.role != "admin":
        query = query.filter(AuditLog.user_id == current_user.id)

    if action:
        query = query.filter(AuditLog.action == action)

    total = query.count()
    logs = query.order_by(desc(AuditLog.created_at)).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "logs": [
            {
                "id": log.id,
                "action": log.action,
                "resource_type": log.resource_type,
                "detail": log.detail,
                "duration_ms": log.duration_ms,
                "status_code": log.status_code,
                "created_at": log.created_at.isoformat() if log.created_at else "",
            }
            for log in logs
        ],
    }
