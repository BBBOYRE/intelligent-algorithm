from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime
import os
import uuid as uuid_mod

from server.auth.security import get_current_user
from server.auth.permissions import require_team_role, ROLE_RANK
from server.models.user import User
from server.models.team import Team, TeamMember
from server.models.task import TeamTask
from server.database import get_db
from config import Config

router = APIRouter()


class TaskCreate(BaseModel):
    title: str
    description: str = ""
    assignee_id: str
    deadline: Optional[str] = None


class TaskStatusUpdate(BaseModel):
    status: str


@router.get("/teams/{team_id}/tasks")
async def list_tasks(
    team_id: str,
    _: TeamMember = Depends(require_team_role("viewer")),
    db: Session = Depends(get_db),
):
    tasks = db.query(TeamTask).filter(TeamTask.team_id == team_id).order_by(TeamTask.created_at.desc()).all()
    user_ids = list(set([t.assignee_id for t in tasks] + [t.assigner_id for t in tasks]))
    users = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()} if user_ids else {}
    team = db.query(Team).filter(Team.id == team_id).first()
    team_name = team.name if team else ""
    return [
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "assignee_id": t.assignee_id,
            "assignee_name": users[t.assignee_id].username if t.assignee_id in users else "unknown",
            "assigner_name": users[t.assigner_id].username if t.assigner_id in users else "unknown",
            "team_name": team_name,
            "status": t.status,
            "deadline": t.deadline.isoformat() + "Z" if t.deadline else None,
            "completion_note": t.completion_note or "",
            "attachment_path": t.attachment_path or "",
            "created_at": t.created_at.isoformat() + "Z" if t.created_at else "",
        }
        for t in tasks
    ]


@router.post("/teams/{team_id}/tasks", status_code=201)
async def create_task(
    team_id: str,
    data: TaskCreate,
    operator: TeamMember = Depends(require_team_role("member")),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    target_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id, TeamMember.user_id == data.assignee_id
    ).first()
    if not target_member:
        raise HTTPException(status_code=404, detail="Assignee is not a team member")
    if ROLE_RANK.get(target_member.role, 0) > ROLE_RANK.get(operator.role, 0):
        raise HTTPException(status_code=403, detail="Cannot assign tasks to higher-role members")

    deadline = None
    if data.deadline:
        try:
            deadline = datetime.fromisoformat(data.deadline.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid deadline format")

    task = TeamTask(
        team_id=team_id,
        title=data.title,
        description=data.description,
        assignee_id=data.assignee_id,
        assigner_id=current_user.id,
        deadline=deadline,
    )
    db.add(task)
    db.commit()
    return {"id": task.id, "title": task.title, "status": task.status}


@router.patch("/teams/{team_id}/tasks/{task_id}")
async def update_task_status(
    team_id: str,
    task_id: str,
    data: TaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = db.query(TeamTask).filter(TeamTask.id == task_id, TeamTask.team_id == team_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if data.status not in ("pending", "in_progress", "completed"):
        raise HTTPException(status_code=400, detail="Invalid status")

    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id, TeamMember.user_id == current_user.id
    ).first()
    is_assignee = task.assignee_id == current_user.id
    is_admin = member and ROLE_RANK.get(member.role, 0) >= ROLE_RANK.get("admin", 0)
    if not is_assignee and not is_admin:
        raise HTTPException(status_code=403, detail="Only assignee or admin can update task status")

    task.status = data.status
    db.commit()
    return {"status": task.status}


@router.post("/teams/{team_id}/tasks/{task_id}/complete")
async def complete_task(
    team_id: str,
    task_id: str,
    completion_note: str = Form(""),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = db.query(TeamTask).filter(TeamTask.id == task_id, TeamTask.team_id == team_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    member = db.query(TeamMember).filter(TeamMember.team_id == team_id, TeamMember.user_id == current_user.id).first()
    is_assignee = task.assignee_id == current_user.id
    is_admin = member and ROLE_RANK.get(member.role, 0) >= ROLE_RANK.get("admin", 0)
    if not is_assignee and not is_admin:
        raise HTTPException(status_code=403, detail="Only assignee or admin can complete task")
    task.status = "completed"
    task.completion_note = completion_note
    if file:
        att_dir = os.path.join(Config.UPLOAD_DIR, "task_attachments")
        os.makedirs(att_dir, exist_ok=True)
        ext = os.path.splitext(file.filename or "")[1]
        fname = f"{task_id}_{uuid_mod.uuid4().hex[:8]}{ext}"
        fpath = os.path.join(att_dir, fname)
        content = await file.read()
        with open(fpath, "wb") as f:
            f.write(content)
        task.attachment_path = fpath
    db.commit()
    return {"status": "completed", "attachment_path": task.attachment_path or ""}


@router.delete("/teams/{team_id}/tasks/{task_id}")
async def delete_task(
    team_id: str,
    task_id: str,
    _: TeamMember = Depends(require_team_role("admin")),
    db: Session = Depends(get_db),
):
    task = db.query(TeamTask).filter(TeamTask.id == task_id, TeamTask.team_id == team_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"status": "deleted"}
