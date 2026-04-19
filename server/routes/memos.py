from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from server.database import get_db
from server.auth.security import get_current_user
from server.models.user import User
from server.models.memo import Memo

router = APIRouter()

class MemoCreate(BaseModel):
    title: str = ""
    content: str = ""
    is_starred: bool = False
    due_date: Optional[datetime] = None

class MemoUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_starred: Optional[bool] = None
    due_date: Optional[datetime] = None

@router.get("/memos")
async def get_memos(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    memos = db.query(Memo).filter(Memo.user_id == current_user.id).order_by(Memo.created_at.desc()).all()
    return memos

@router.post("/memos")
async def create_memo(data: MemoCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Fallback to truncated content if title is empty
    title = data.title.strip()
    if not title and data.content:
        first_line = data.content.split("\n")[0]
        title = first_line[:50]

    memo = Memo(
        user_id=current_user.id,
        title=title,
        content=data.content,
        is_starred=data.is_starred,
        due_date=data.due_date
    )
    db.add(memo)
    db.commit()
    db.refresh(memo)
    return memo

@router.patch("/memos/{memo_id}")
async def update_memo(memo_id: str, data: MemoUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    memo = db.query(Memo).filter(Memo.id == memo_id, Memo.user_id == current_user.id).first()
    if not memo:
        raise HTTPException(status_code=404, detail="备忘录不存在或无权访问")
    
    if data.title is not None:
        memo.title = data.title
    if data.content is not None:
        memo.content = data.content
    if data.is_starred is not None:
        memo.is_starred = data.is_starred
    
    # due_date can be explicitly set to None, so we should check for key presence.
    # However, BaseModel Optional[datetime] without `.dict(exclude_unset=True)` makes it tricky.
    # A simple way is to check the fields set.
    update_data = data.dict(exclude_unset=True)
    if "due_date" in update_data:
        memo.due_date = update_data["due_date"]
    
    db.commit()
    db.refresh(memo)
    return memo

@router.delete("/memos/{memo_id}", status_code=204)
async def delete_memo(memo_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    memo = db.query(Memo).filter(Memo.id == memo_id, Memo.user_id == current_user.id).first()
    if not memo:
        raise HTTPException(status_code=404, detail="备忘录不存在或无权访问")
    
    db.delete(memo)
    db.commit()
