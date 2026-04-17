from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from server.database import get_db
from server.auth.security import get_current_user
from server.auth.permissions import require_team_role, ROLE_RANK
from server.models.user import User
from server.models.team import Team, TeamMember

router = APIRouter()


# ---------- Schemas ----------

class TeamCreate(BaseModel):
    name: str
    description: Optional[str] = ""


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class InviteMember(BaseModel):
    email: str
    role: str = "member"  # member / admin / viewer


class UpdateMemberRole(BaseModel):
    role: str


# ---------- Helpers ----------

def _team_detail(team: Team, db: Session) -> dict:
    members = db.query(TeamMember).filter(TeamMember.team_id == team.id).all()
    user_ids = [m.user_id for m in members]
    users = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()}
    return {
        "id": team.id,
        "name": team.name,
        "description": team.description,
        "owner_id": team.owner_id,
        "created_at": team.created_at.isoformat(),
        "member_count": len(members),
        "members": [
            {
                "user_id": m.user_id,
                "username": users[m.user_id].username if m.user_id in users else "未知",
                "email": users[m.user_id].email if m.user_id in users else "",
                "role": m.role,
                "joined_at": m.joined_at.isoformat(),
            }
            for m in members
        ],
    }


# ---------- Routes ----------

@router.get("/teams")
async def list_teams(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """列出当前用户所在的所有团队"""
    memberships = db.query(TeamMember).filter(TeamMember.user_id == current_user.id).all()
    team_ids = [m.team_id for m in memberships]
    teams = db.query(Team).filter(Team.id.in_(team_ids)).all()
    role_map = {m.team_id: m.role for m in memberships}
    return [
        {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "owner_id": t.owner_id,
            "my_role": role_map.get(t.id, "member"),
            "created_at": t.created_at.isoformat(),
        }
        for t in teams
    ]


@router.post("/teams", status_code=201)
async def create_team(
    data: TeamCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    team = Team(name=data.name, description=data.description or "", owner_id=current_user.id)
    db.add(team)
    db.flush()

    # 创建者自动成为 owner
    db.add(TeamMember(team_id=team.id, user_id=current_user.id, role="owner"))
    db.commit()
    db.refresh(team)
    return _team_detail(team, db)


@router.get("/teams/{team_id}")
async def get_team(
    team_id: str,
    _: TeamMember = Depends(require_team_role("viewer")),
    db: Session = Depends(get_db),
):
    team = db.query(Team).filter(Team.id == team_id).first()
    return _team_detail(team, db)


@router.patch("/teams/{team_id}")
async def update_team(
    team_id: str,
    data: TeamUpdate,
    _: TeamMember = Depends(require_team_role("admin")),
    db: Session = Depends(get_db),
):
    team = db.query(Team).filter(Team.id == team_id).first()
    if data.name is not None:
        team.name = data.name
    if data.description is not None:
        team.description = data.description
    db.commit()
    db.refresh(team)
    return _team_detail(team, db)


@router.delete("/teams/{team_id}", status_code=204)
async def delete_team(
    team_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")
    if team.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="只有团队所有者可以解散团队")
    db.query(TeamMember).filter(TeamMember.team_id == team_id).delete()
    db.delete(team)
    db.commit()


@router.post("/teams/{team_id}/members", status_code=201)
async def invite_member(
    team_id: str,
    data: InviteMember,
    _: TeamMember = Depends(require_team_role("admin")),
    db: Session = Depends(get_db),
):
    if data.role not in ("viewer", "member", "admin"):
        raise HTTPException(status_code=400, detail="无效的角色，可选：viewer / member / admin")

    target = db.query(User).filter(User.email == data.email).first()
    if not target:
        raise HTTPException(status_code=404, detail="用户不存在")

    existing = db.query(TeamMember).filter(
        TeamMember.team_id == team_id, TeamMember.user_id == target.id
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="该用户已是团队成员")

    db.add(TeamMember(team_id=team_id, user_id=target.id, role=data.role))
    db.commit()
    return {"detail": "邀请成功", "user_id": target.id, "role": data.role}


@router.patch("/teams/{team_id}/members/{user_id}")
async def update_member_role(
    team_id: str,
    user_id: str,
    data: UpdateMemberRole,
    current_user: User = Depends(get_current_user),
    operator: TeamMember = Depends(require_team_role("admin")),
    db: Session = Depends(get_db),
):
    if data.role not in ("viewer", "member", "admin"):
        raise HTTPException(status_code=400, detail="无效的角色")

    target_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id, TeamMember.user_id == user_id
    ).first()
    if not target_member:
        raise HTTPException(status_code=404, detail="成员不存在")
    if target_member.role == "owner":
        raise HTTPException(status_code=403, detail="不能修改所有者角色，请使用转让所有权接口")
    if ROLE_RANK.get(data.role, 0) >= ROLE_RANK.get(operator.role, 0):
        raise HTTPException(status_code=403, detail="不能设置高于或等于自身的角色")

    target_member.role = data.role
    db.commit()
    return {"detail": "角色已更新", "role": data.role}


@router.delete("/teams/{team_id}/members/{user_id}", status_code=204)
async def remove_member(
    team_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")

    # 只有 admin/owner 或本人可以移除
    operator = db.query(TeamMember).filter(
        TeamMember.team_id == team_id, TeamMember.user_id == current_user.id
    ).first()
    is_self = current_user.id == user_id
    is_admin = operator and ROLE_RANK.get(operator.role, 0) >= ROLE_RANK["admin"]
    if not is_self and not is_admin:
        raise HTTPException(status_code=403, detail="权限不足")

    target = db.query(TeamMember).filter(
        TeamMember.team_id == team_id, TeamMember.user_id == user_id
    ).first()
    if not target:
        raise HTTPException(status_code=404, detail="成员不存在")
    if target.role == "owner":
        raise HTTPException(status_code=403, detail="不能移除所有者，请先转让所有权")

    db.delete(target)
    db.commit()


@router.post("/teams/{team_id}/transfer")
async def transfer_ownership(
    team_id: str,
    data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """转让团队所有权给另一个成员"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")
    if team.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="只有所有者可以转让")

    new_owner_id = data.get("new_owner_id")
    if not new_owner_id:
        raise HTTPException(status_code=400, detail="缺少 new_owner_id")

    new_owner_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id, TeamMember.user_id == new_owner_id
    ).first()
    if not new_owner_member:
        raise HTTPException(status_code=404, detail="目标用户不是团队成员")

    # 降级原所有者为 admin，升级新所有者
    old_owner_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id, TeamMember.user_id == current_user.id
    ).first()
    if old_owner_member:
        old_owner_member.role = "admin"
    new_owner_member.role = "owner"
    team.owner_id = new_owner_id
    db.commit()
    return {"detail": "所有权已转让"}
