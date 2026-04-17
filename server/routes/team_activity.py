from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from server.database import get_db
from server.auth.security import get_current_user
from server.auth.permissions import require_team_role
from server.models.user import User
from server.models.team import Team, TeamMember
from server.models.audit_log import AuditLog

router = APIRouter()


@router.get("/teams/{team_id}/activity")
async def get_team_activity(
    team_id: str,
    limit: int = 30,
    _: TeamMember = Depends(require_team_role("viewer")),
    db: Session = Depends(get_db),
):
    members = db.query(TeamMember).filter(TeamMember.team_id == team_id).all()
    member_ids = [m.user_id for m in members]
    if not member_ids:
        return []

    users = {u.id: u for u in db.query(User).filter(User.id.in_(member_ids)).all()}

    logs = (
        db.query(AuditLog)
        .filter(AuditLog.user_id.in_(member_ids))
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "username": users.get(log.user_id, None) and users[log.user_id].username or "未知",
            "action": log.action,
            "resource_type": log.resource_type,
            "details": log.detail,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]
