import secrets
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from server.database import get_db
from server.auth.security import get_current_user, hash_password
from server.models.user import User
from server.models.api_key import ApiKey

router = APIRouter()


class ApiKeyCreate(BaseModel):
    name: str


@router.post("/api-keys", status_code=201)
async def create_api_key(
    data: ApiKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not data.name.strip():
        raise HTTPException(status_code=400, detail="请输入 Key 名称")

    raw_key = "sk-" + secrets.token_hex(24)
    prefix = raw_key[:12]

    api_key = ApiKey(
        user_id=current_user.id,
        name=data.name.strip(),
        key_hash=hash_password(raw_key),
        key_prefix=prefix,
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    return {
        "id": api_key.id,
        "name": api_key.name,
        "key": raw_key,
        "prefix": prefix,
        "created_at": api_key.created_at.isoformat(),
    }


@router.get("/api-keys")
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    keys = (
        db.query(ApiKey)
        .filter(ApiKey.user_id == current_user.id, ApiKey.is_active == True)
        .order_by(ApiKey.created_at.desc())
        .all()
    )
    return [
        {
            "id": k.id,
            "name": k.name,
            "prefix": k.key_prefix,
            "last_used_at": k.last_used_at.isoformat() if k.last_used_at else None,
            "created_at": k.created_at.isoformat(),
        }
        for k in keys
    ]


@router.delete("/api-keys/{key_id}", status_code=204)
async def delete_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    api_key = db.query(ApiKey).filter(
        ApiKey.id == key_id, ApiKey.user_id == current_user.id
    ).first()
    if not api_key:
        raise HTTPException(status_code=404, detail="API Key 不存在")
    db.delete(api_key)
    db.commit()
