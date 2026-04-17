from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from config import Config
from server.database import get_db
from server.models.user import User

security_scheme = HTTPBearer(auto_error=False)

DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000000"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=Config.JWT_EXPIRE_MINUTES))
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM)


def _get_or_create_default_user(db: Session) -> User:
    """私有化部署免登录时使用的默认用户"""
    user = db.query(User).filter(User.id == DEFAULT_USER_ID).first()
    if not user:
        user = User(
            id=DEFAULT_USER_ID,
            email="admin@local",
            username="本地用户",
            hashed_password=hash_password("admin"),
            role="admin",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    if Config.AUTH_DISABLED:
        return _get_or_create_default_user(db)

    # 1) JWT auth
    if credentials is not None:
        token = credentials.credentials
        try:
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的认证凭据")
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="认证凭据已过期或无效")

        user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已禁用")
        return user

    # 2) API Key auth via X-API-Key header
    api_key_raw = request.headers.get("X-API-Key")
    if api_key_raw:
        from server.models.api_key import ApiKey
        keys = db.query(ApiKey).filter(ApiKey.is_active == True, ApiKey.key_prefix == api_key_raw[:12]).all()
        for k in keys:
            if verify_password(api_key_raw, k.key_hash):
                k.last_used_at = datetime.now(timezone.utc)
                db.commit()
                user = db.query(User).filter(User.id == k.user_id, User.is_active == True).first()
                if user is None:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API Key 对应的用户已禁用")
                return user
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的 API Key")

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未提供认证凭据")
