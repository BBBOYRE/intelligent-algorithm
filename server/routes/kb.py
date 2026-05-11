from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from server.database import get_db
from server.auth.security import get_current_user
from server.models.user import User
from server.models.knowledge_base_model import KnowledgeBaseModel
from server.models.kb_permission import KBPermission
from server.models.team import Team, TeamMember
from server.dependencies import get_kb, reset_kb

router = APIRouter()


class KBCreateRequest(BaseModel):
    name: str
    description: str = ""
    team_id: Optional[str] = None
    visibility: str = "all"


class KBPermissionRequest(BaseModel):
    user_id: str
    permission: str = "read"


# ---- Permission helpers ----

def _resolve_kb(kb_id: str, user: User, db: Session, required: str = "read"):
    """Resolve a KB model and check access. required: read/write/admin"""
    kb_model = db.query(KnowledgeBaseModel).filter(KnowledgeBaseModel.id == kb_id).first()
    if not kb_model:
        raise HTTPException(status_code=404, detail="知识库不存在")

    # Personal KB: owner only
    if not kb_model.team_id:
        if kb_model.user_id != user.id:
            raise HTTPException(status_code=403, detail="无权访问此知识库")
        return kb_model

    # Team KB: check team membership
    member = db.query(TeamMember).filter(
        TeamMember.team_id == kb_model.team_id, TeamMember.user_id == user.id
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="你不是该团队成员")

    PERM_RANK = {"read": 0, "write": 1, "admin": 2}
    req_rank = PERM_RANK.get(required, 0)

    # Team owner/admin always have full access
    if member.role in ("owner", "admin"):
        return kb_model

    # visibility=all: all members can read, members+ can write
    if kb_model.visibility == "all":
        if required == "admin":
            raise HTTPException(status_code=403, detail="需要管理员权限")
        if required == "write" and member.role == "viewer":
            raise HTTPException(status_code=403, detail="观察者无写入权限")
        return kb_model

    # visibility=restricted: check KBPermission
    perm = db.query(KBPermission).filter(
        KBPermission.kb_id == kb_id, KBPermission.user_id == user.id
    ).first()
    if not perm or PERM_RANK.get(perm.permission, 0) < req_rank:
        raise HTTPException(status_code=403, detail="无权访问此知识库")
    return kb_model


def _get_kb_instance(kb_model: KnowledgeBaseModel, user: User):
    if kb_model.team_id:
        return get_kb(user.id, kb_model.id, team_id=kb_model.team_id)
    return get_kb(user.id, kb_model.id)


# ---- Routes ----

@router.get("/kb/list")
async def list_knowledge_bases(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Personal KBs
    personal = db.query(KnowledgeBaseModel).filter(
        KnowledgeBaseModel.user_id == current_user.id,
        KnowledgeBaseModel.team_id == None,
    ).all()

    # Create a default personal KB if none exists
    if not personal:
        kb_id = str(uuid.uuid4())
        default_kb = KnowledgeBaseModel(
            id=kb_id,
            user_id=current_user.id,
            name="我的项目",
            collection_name=f"kb_{current_user.id}_{kb_id}",
            description="默认个人项目",
            visibility="all",
            created_by=current_user.id,
        )
        db.add(default_kb)
        db.commit()
        db.refresh(default_kb)
        personal = [default_kb]

    # Team KBs: find all teams user belongs to
    memberships = db.query(TeamMember).filter(TeamMember.user_id == current_user.id).all()
    team_ids = [m.team_id for m in memberships]
    team_kbs = []
    if team_ids:
        all_team_kbs = db.query(KnowledgeBaseModel).filter(
            KnowledgeBaseModel.team_id.in_(team_ids)
        ).all()
        for kb_model in all_team_kbs:
            if kb_model.visibility == "all":
                team_kbs.append(kb_model)
            else:
                perm = db.query(KBPermission).filter(
                    KBPermission.kb_id == kb_model.id, KBPermission.user_id == current_user.id
                ).first()
                member = next((m for m in memberships if m.team_id == kb_model.team_id), None)
                if perm or (member and member.role in ("owner", "admin")):
                    team_kbs.append(kb_model)

    # Get team names
    teams = {}
    if team_ids:
        for t in db.query(Team).filter(Team.id.in_(team_ids)).all():
            teams[t.id] = t.name

    result = []
    for kb_model in personal + team_kbs:
        try:
            kb = _get_kb_instance(kb_model, current_user)
            stats = kb.get_stats()
            doc_list = [
                {"file_name": d.get("file_name", "unknown"), "format": d.get("metadata", {}).get("format", "")}
                for d in kb.all_parsed_docs
            ]
        except Exception:
            stats = {"total_chunks": 0}
            doc_list = []
        result.append({
            "id": kb_model.id,
            "name": kb_model.name,
            "collection_name": kb_model.collection_name,
            "description": kb_model.description,
            "team_id": kb_model.team_id,
            "team_name": teams.get(kb_model.team_id, "") if kb_model.team_id else None,
            "visibility": kb_model.visibility,
            "created_by": kb_model.created_by,
            "total_chunks": stats.get("total_chunks", 0),
            "documents": doc_list,
        })
    return {"knowledge_bases": result}


@router.post("/kb/create")
async def create_knowledge_base(
    data: KBCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    kb_id = str(uuid.uuid4())
    if data.team_id:
        member = db.query(TeamMember).filter(
            TeamMember.team_id == data.team_id, TeamMember.user_id == current_user.id
        ).first()
        if not member or member.role not in ("owner", "admin"):
            raise HTTPException(status_code=403, detail="只有团队管理员可以创建团队知识库")
        collection_name = f"kb_team_{data.team_id}_{kb_id}"
    else:
        collection_name = f"kb_{current_user.id}_{kb_id}"

    kb_model = KnowledgeBaseModel(
        id=kb_id,
        user_id=current_user.id,
        name=data.name,
        collection_name=collection_name,
        description=data.description,
        team_id=data.team_id,
        visibility=data.visibility if data.team_id else "all",
        created_by=current_user.id,
    )
    db.add(kb_model)
    db.commit()
    return {"status": "success", "id": kb_model.id, "name": kb_model.name}


class KBUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    visibility: Optional[str] = None


@router.patch("/kb/{kb_id}")
async def update_knowledge_base(
    kb_id: str,
    data: KBUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    kb_model = _resolve_kb(kb_id, current_user, db, required="admin")
    if data.name is not None:
        kb_model.name = data.name
    if data.description is not None:
        kb_model.description = data.description
    if data.visibility is not None and data.visibility in ("all", "restricted"):
        kb_model.visibility = data.visibility
    db.commit()
    return {"status": "success", "id": kb_model.id, "name": kb_model.name}


@router.delete("/kb/{kb_id}")
async def delete_knowledge_base(
    kb_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    kb_model = _resolve_kb(kb_id, current_user, db, required="admin")
    try:
        kb = _get_kb_instance(kb_model, current_user)
        kb.collection.delete(where={})
        kb.all_parsed_docs.clear()
        if kb.docs_storage_file.exists():
            kb.docs_storage_file.write_text("[]", encoding="utf-8")
    except Exception:
        pass
    db.query(KBPermission).filter(KBPermission.kb_id == kb_id).delete()
    db.delete(kb_model)
    db.commit()
    return {"status": "success", "message": f"知识库 '{kb_model.name}' 已删除"}


@router.get("/kb/documents")
async def list_kb_documents(
    kb_id: str = "default",
    query: str = "",
    file_format: str = "",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if kb_id != "default":
        _resolve_kb(kb_id, current_user, db, required="read")
    try:
        kb_model = db.query(KnowledgeBaseModel).filter(KnowledgeBaseModel.id == kb_id).first() if kb_id != "default" else None
        if kb_model and kb_model.team_id:
            kb = get_kb(current_user.id, kb_id, team_id=kb_model.team_id)
        else:
            kb = get_kb(current_user.id, kb_id)
        docs = kb.search_documents(query=query, file_format=file_format)
        return {"documents": docs}
    except Exception as exc:
        return {"documents": [], "error": str(exc)}


@router.delete("/kb/documents/{file_name}")
async def delete_kb_document(
    file_name: str,
    kb_id: str = "default",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if kb_id != "default":
        _resolve_kb(kb_id, current_user, db, required="write")
    try:
        kb_model = db.query(KnowledgeBaseModel).filter(KnowledgeBaseModel.id == kb_id).first() if kb_id != "default" else None
        if kb_model and kb_model.team_id:
            kb = get_kb(current_user.id, kb_id, team_id=kb_model.team_id)
        else:
            kb = get_kb(current_user.id, kb_id)
        removed = kb.remove_document(file_name)
        if removed:
            return {"status": "success", "message": f"文档 '{file_name}' 已删除"}
        raise HTTPException(status_code=404, detail="文档不存在")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/kb/stats")
async def get_kb_stats(
    kb_id: str = "default",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        # 默认 kb_id="default" 时，汇总当前用户所有知识库的统计
        if kb_id == "default":
            return _aggregate_user_stats(current_user, db)

        kb_model = db.query(KnowledgeBaseModel).filter(KnowledgeBaseModel.id == kb_id).first() if kb_id != "default" else None
        if kb_model and kb_model.team_id:
            kb = get_kb(current_user.id, kb_id, team_id=kb_model.team_id)
        else:
            kb = get_kb(current_user.id, kb_id)
        stats = kb.get_stats()
        doc_list = [
            {"file_name": d.get("file_name", "unknown"), "format": d.get("metadata", {}).get("format", "")}
            for d in kb.all_parsed_docs
        ]
        return {**stats, "documents": doc_list}
    except Exception as exc:
        return {"total_chunks": 0, "documents": [], "error": str(exc)}


def _aggregate_user_stats(current_user: User, db: Session) -> dict:
    """汇总当前用户所有知识库（个人 + 项目）的统计数据"""
    # 查找该用户的所有 KnowledgeBaseModel（项目级 KB）
    kb_models = db.query(KnowledgeBaseModel).filter(
        KnowledgeBaseModel.user_id == current_user.id
    ).all()

    total_chunks = 0
    total_docs = 0
    all_docs: list[dict] = []

    # 2) 个人默认 KB
    default_kb = get_kb(current_user.id, "default")
    s = default_kb.get_stats()
    total_chunks += s.get("total_chunks", 0)
    total_docs += s.get("document_count", 0)
    all_docs.extend(
        {"file_name": d.get("file_name", "unknown"), "format": d.get("metadata", {}).get("format", "")}
        for d in default_kb.all_parsed_docs
    )

    # 3) 项目 KB
    seen_kb_ids = set()
    for m in kb_models:
        if m.id in seen_kb_ids:
            continue
        seen_kb_ids.add(m.id)
        try:
            if m.team_id:
                kb = get_kb(current_user.id, m.id, team_id=m.team_id)
            else:
                kb = get_kb(current_user.id, m.id)
            s = kb.get_stats()
            total_chunks += s.get("total_chunks", 0)
            total_docs += s.get("document_count", 0)
            all_docs.extend(
                {"file_name": d.get("file_name", "unknown"), "format": d.get("metadata", {}).get("format", "")}
                for d in kb.all_parsed_docs
            )
        except Exception:
            continue

    return {
        "total_chunks": total_chunks,
        "document_count": total_docs,
        "documents": all_docs,
    }


@router.delete("/kb/clear")
async def clear_kb(
    kb_id: str = "default",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if kb_id != "default":
        _resolve_kb(kb_id, current_user, db, required="write")
    try:
        kb_model = db.query(KnowledgeBaseModel).filter(KnowledgeBaseModel.id == kb_id).first() if kb_id != "default" else None
        if kb_model and kb_model.team_id:
            kb = get_kb(current_user.id, kb_id, team_id=kb_model.team_id)
        else:
            kb = get_kb(current_user.id, kb_id)
        kb.collection.delete(where={})
        kb.all_parsed_docs.clear()
        kb.docs_storage_file.write_text("[]", encoding="utf-8")
        return {"status": "success", "message": "知识库已清空"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ---- Permission management ----

@router.get("/kb/{kb_id}/permissions")
async def list_kb_permissions(
    kb_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    kb_model = _resolve_kb(kb_id, current_user, db, required="admin")
    perms = db.query(KBPermission).filter(KBPermission.kb_id == kb_id).all()
    user_ids = [p.user_id for p in perms]
    users = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()} if user_ids else {}
    return [
        {
            "user_id": p.user_id,
            "username": users[p.user_id].username if p.user_id in users else "未知",
            "email": users[p.user_id].email if p.user_id in users else "",
            "permission": p.permission,
        }
        for p in perms
    ]


@router.post("/kb/{kb_id}/permissions")
async def set_kb_permission(
    kb_id: str,
    data: KBPermissionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    kb_model = _resolve_kb(kb_id, current_user, db, required="admin")
    if data.permission not in ("read", "write", "admin"):
        raise HTTPException(status_code=400, detail="权限值无效")
    existing = db.query(KBPermission).filter(
        KBPermission.kb_id == kb_id, KBPermission.user_id == data.user_id
    ).first()
    if existing:
        existing.permission = data.permission
    else:
        db.add(KBPermission(kb_id=kb_id, user_id=data.user_id, permission=data.permission))
    db.commit()
    return {"status": "success"}


@router.delete("/kb/{kb_id}/permissions/{user_id}")
async def remove_kb_permission(
    kb_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _resolve_kb(kb_id, current_user, db, required="admin")
    perm = db.query(KBPermission).filter(
        KBPermission.kb_id == kb_id, KBPermission.user_id == user_id
    ).first()
    if perm:
        db.delete(perm)
        db.commit()
    return {"status": "success"}
