from fastapi import APIRouter, Depends, HTTPException
from server.auth.security import get_current_user
from server.models.user import User
from server.tasks.task_manager import task_manager

router = APIRouter()


@router.get("/tasks/{task_id}")
async def get_task(task_id: str, current_user: User = Depends(get_current_user)):
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task.to_dict()


@router.get("/tasks")
async def list_tasks(current_user: User = Depends(get_current_user)):
    return {"tasks": task_manager.list_tasks()}
