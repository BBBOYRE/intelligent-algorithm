from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from server.auth.security import get_current_user
from server.auth.permissions import require_team_role
from server.models.user import User
from server.models.team import TeamMember
from server.models.announcement import TeamAnnouncement
from server.database import get_db

router = APIRouter()


class AnnouncementCreate(BaseModel):
    content: str


@router.get("/teams/{team_id}/announcements")
async def list_announcements(
    team_id: str,
    _: TeamMember = Depends(require_team_role("viewer")),
    db: Session = Depends(get_db),
):
    items = db.query(TeamAnnouncement).filter(
        TeamAnnouncement.team_id == team_id
    ).order_by(TeamAnnouncement.created_at.desc()).all()
    user_ids = list(set(a.author_id for a in items))
    users = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()} if user_ids else {}
    return [
        {
            "id": a.id,
            "content": a.content,
            "author_name": users[a.author_id].username if a.author_id in users else "unknown",
            "created_at": a.created_at.isoformat() + "Z" if a.created_at else "",
        }
        for a in items
    ]


@router.post("/teams/{team_id}/announcements", status_code=201)
async def create_announcement(
    team_id: str,
    data: AnnouncementCreate,
    _: TeamMember = Depends(require_team_role("admin")),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not data.content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty")
    ann = TeamAnnouncement(team_id=team_id, author_id=current_user.id, content=data.content.strip())
    db.add(ann)
    db.commit()
    return {"id": ann.id, "content": ann.content, "author_name": current_user.username, "created_at": ann.created_at.isoformat() + "Z"}


@router.delete("/teams/{team_id}/announcements/{ann_id}")
async def delete_announcement(
    team_id: str,
    ann_id: str,
    _: TeamMember = Depends(require_team_role("admin")),
    db: Session = Depends(get_db),
):
    ann = db.query(TeamAnnouncement).filter(TeamAnnouncement.id == ann_id, TeamAnnouncement.team_id == team_id).first()
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")
    db.delete(ann)
    db.commit()
    return {"status": "deleted"}
