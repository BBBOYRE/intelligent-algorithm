from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    email: str
    username: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserProfile"


class UserProfile(BaseModel):
    id: str
    email: str
    username: str
    role: str
    avatar: Optional[str] = ""
    bio: Optional[str] = ""

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    username: Optional[str] = None
    bio: Optional[str] = None


TokenResponse.model_rebuild()
