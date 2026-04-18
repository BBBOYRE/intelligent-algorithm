from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import os
import uuid

from server.database import get_db
from server.auth.security import hash_password, verify_password, create_access_token, get_current_user
from server.auth.schemas import UserCreate, UserLogin, TokenResponse, UserProfile, ProfileUpdate
from server.models.user import User
from config import Config

router = APIRouter()


@router.post("/auth/register", response_model=TokenResponse)
async def register(data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="该邮箱已注册")

    user = User(
        email=data.email,
        username=data.username,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    return TokenResponse(
        access_token=token,
        user=UserProfile.model_validate(user),
    )


@router.post("/auth/login", response_model=TokenResponse)
async def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已被禁用")

    token = create_access_token(user.id)
    return TokenResponse(
        access_token=token,
        user=UserProfile.model_validate(user),
    )


@router.get("/auth/me", response_model=UserProfile)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserProfile.model_validate(current_user)


@router.put("/auth/profile", response_model=UserProfile)
async def update_profile(data: ProfileUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if data.username is not None:
        current_user.username = data.username
    if data.bio is not None:
        current_user.bio = data.bio
    db.commit()
    db.refresh(current_user)
    return UserProfile.model_validate(current_user)


@router.post("/auth/avatar")
async def upload_avatar(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    avatar_dir = os.path.join(Config.UPLOAD_DIR, "avatars")
    os.makedirs(avatar_dir, exist_ok=True)
    ext = os.path.splitext(file.filename or "")[1] or ".png"
    filename = f"{current_user.id}_{uuid.uuid4().hex[:8]}{ext}"
    filepath = os.path.join(avatar_dir, filename)
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)
    current_user.avatar = f"/api/files/avatar/{filename}"
    db.commit()
    return {"avatar": current_user.avatar}
