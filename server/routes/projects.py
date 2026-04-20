from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
import uuid

from server.auth.security import get_current_user
from server.models.user import User
from server.models.project import Project
from server.models.team import TeamMember
from server.models.knowledge_base_model import KnowledgeBaseModel
from server.models.kb_permission import KBPermission
from server.database import get_db
from server.dependencies import get_kb

router = APIRouter()


class ProjectCreate(BaseModel):
    name: str
    description: str = ""
    team_id: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


@router.get("/projects")
async def list_projects(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    personal = db.query(Project).filter(Project.owner_id == current_user.id, Project.is_personal == True).all()
    memberships = db.query(TeamMember).filter(TeamMember.user_id == current_user.id).all()
    team_ids = [m.team_id for m in memberships]
    team_projects = []
    if team_ids:
        team_projects = db.query(Project).filter(Project.team_id.in_(team_ids), Project.is_personal == False).all()
    result = []
    for p in personal + team_projects:
        kb_count = db.query(KnowledgeBaseModel).filter(KnowledgeBaseModel.project_id == p.id).count()
        result.append({
            "id": p.id, "name": p.name, "description": p.description,
            "owner_id": p.owner_id, "team_id": p.team_id,
            "is_personal": p.is_personal, "kb_count": kb_count,
            "created_at": p.created_at.isoformat() + "Z" if p.created_at else "",
            "updated_at": p.updated_at.isoformat() + "Z" if p.updated_at else "",
        })
    return result


@router.post("/projects", status_code=201)
async def create_project(data: ProjectCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not data.name.strip():
        raise HTTPException(status_code=400, detail="Project name required")
    is_personal = not bool(data.team_id)
    if data.team_id:
        member = db.query(TeamMember).filter(TeamMember.team_id == data.team_id, TeamMember.user_id == current_user.id).first()
        if not member or member.role not in ("owner", "admin"):
            raise HTTPException(status_code=403, detail="Only team admin can create team projects")
    proj = Project(name=data.name.strip(), description=data.description, owner_id=current_user.id, team_id=data.team_id, is_personal=is_personal)
    db.add(proj)
    db.flush()

    kb_id = str(uuid.uuid4())
    if data.team_id:
        collection_name = f"kb_team_{data.team_id}_{kb_id}"
    else:
        collection_name = f"kb_{current_user.id}_{kb_id}"
    kb = KnowledgeBaseModel(
        id=kb_id,
        user_id=current_user.id,
        name=data.name.strip(),
        collection_name=collection_name,
        description=data.description,
        team_id=data.team_id,
        visibility="all",
        project_id=proj.id,
        created_by=current_user.id,
    )
    db.add(kb)
    db.commit()
    db.refresh(proj)
    return {"id": proj.id, "name": proj.name, "kb_id": kb_id}


@router.get("/projects/{project_id}")
async def get_project(project_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    kbs = db.query(KnowledgeBaseModel).filter(KnowledgeBaseModel.project_id == project_id).all()
    owner = db.query(User).filter(User.id == proj.owner_id).first()
    kb_list = []
    for kb_model in kbs:
        try:
            kb_inst = get_kb(current_user.id, kb_model.id, team_id=kb_model.team_id)
            stats = kb_inst.get_stats()
            doc_count = len(kb_inst.all_parsed_docs)
        except Exception:
            stats = {"total_chunks": 0}
            doc_count = 0
        kb_list.append({
            "id": kb_model.id, "name": kb_model.name,
            "description": kb_model.description,
            "total_chunks": stats.get("total_chunks", 0),
            "doc_count": doc_count,
        })
    primary_kb_id = kbs[0].id if kbs else None
    return {
        "id": proj.id, "name": proj.name, "description": proj.description,
        "owner_id": proj.owner_id, "owner_name": owner.username if owner else "",
        "team_id": proj.team_id, "is_personal": proj.is_personal,
        "knowledge_bases": kb_list,
        "kb_id": primary_kb_id,
        "created_at": proj.created_at.isoformat() + "Z" if proj.created_at else "",
        "updated_at": proj.updated_at.isoformat() + "Z" if proj.updated_at else "",
    }


@router.patch("/projects/{project_id}")
async def update_project(project_id: str, data: ProjectUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    if proj.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only owner can edit")
    if data.name is not None:
        proj.name = data.name
        kb = db.query(KnowledgeBaseModel).filter(KnowledgeBaseModel.project_id == project_id).first()
        if kb:
            kb.name = data.name
    if data.description is not None:
        proj.description = data.description
    db.commit()
    return {"status": "success"}


@router.delete("/projects/{project_id}")
async def delete_project(project_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    if proj.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only owner can delete")

    kbs = db.query(KnowledgeBaseModel).filter(KnowledgeBaseModel.project_id == project_id).all()
    for kb_model in kbs:
        try:
            kb_inst = get_kb(current_user.id, kb_model.id, team_id=kb_model.team_id)
            kb_inst.collection.delete(where={})
            kb_inst.all_parsed_docs.clear()
            if kb_inst.docs_storage_file.exists():
                kb_inst.docs_storage_file.write_text("[]", encoding="utf-8")
        except Exception:
            pass
        db.query(KBPermission).filter(KBPermission.kb_id == kb_model.id).delete()
        db.delete(kb_model)

    db.delete(proj)
    db.commit()
    return {"status": "deleted"}
