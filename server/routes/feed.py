from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from server.auth.security import get_current_user
from server.models.user import User
from server.models.audit_log import AuditLog
from server.models.announcement import TeamAnnouncement
from server.models.task import TeamTask
from server.models.team import TeamMember
from server.database import get_db

router = APIRouter()


@router.get("/feed")
async def get_feed(
    limit: int = Query(30, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = []

    logs = db.query(AuditLog).filter(AuditLog.user_id == current_user.id).order_by(AuditLog.created_at.desc()).limit(limit).all()
    for log in logs:
        items.append({
            "type": "activity",
            "title": log.action,
            "detail": log.detail or "",
            "created_at": log.created_at.isoformat() + "Z" if log.created_at else "",
        })

    memberships = db.query(TeamMember).filter(TeamMember.user_id == current_user.id).all()
    team_ids = [m.team_id for m in memberships]

    if team_ids:
        anns = db.query(TeamAnnouncement).filter(TeamAnnouncement.team_id.in_(team_ids)).order_by(TeamAnnouncement.created_at.desc()).limit(10).all()
        user_ids = list(set(a.author_id for a in anns))
        users = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()} if user_ids else {}
        for a in anns:
            items.append({
                "type": "announcement",
                "title": "团队公告",
                "detail": a.content,
                "author": users[a.author_id].username if a.author_id in users else "",
                "created_at": a.created_at.isoformat() + "Z" if a.created_at else "",
            })

    my_tasks = db.query(TeamTask).filter(TeamTask.assignee_id == current_user.id, TeamTask.status != "completed").all()
    for t in my_tasks:
        items.append({
            "type": "task",
            "title": f"待办: {t.title}",
            "detail": f"状态: {t.status}" + (f" · 截止: {t.deadline.strftime('%Y-%m-%d')}" if t.deadline else ""),
            "created_at": t.created_at.isoformat() + "Z" if t.created_at else "",
        })

    items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return items[:limit]
