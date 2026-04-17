from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from server.database import get_db
from server.auth.security import get_current_user
from server.models.user import User
from server.models.team import Team, TeamMember

ROLE_RANK = {"viewer": 0, "member": 1, "admin": 2, "owner": 3}


def _get_member(db: Session, team_id: str, user_id: str) -> TeamMember | None:
    return db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == user_id,
    ).first()


def require_team_role(min_role: str = "member"):
    """路由依赖：要求当前用户在指定团队中拥有不低于 min_role 的角色。
    用法：在路由参数中加 team_id: str，再 Depends(require_team_role("admin"))
    """
    async def checker(
        team_id: str,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> TeamMember:
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail="团队不存在")

        member = _get_member(db, team_id, current_user.id)
        if not member:
            raise HTTPException(status_code=403, detail="你不是该团队成员")

        if ROLE_RANK.get(member.role, 0) < ROLE_RANK.get(min_role, 0):
            raise HTTPException(status_code=403, detail=f"需要 {min_role} 及以上权限")

        return member

    return checker
