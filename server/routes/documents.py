import asyncio
import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from utils.file_utils import save_uploaded_file_fastapi
from server.auth.security import get_current_user
from server.models.user import User
from server.dependencies import get_kb
from server.tasks.task_manager import task_manager
from server.tasks.document_tasks import process_document_batch

router = APIRouter()


@router.post("/documents/upload")
async def upload_documents(
    files: list[UploadFile] = File(...),
    kb_id: str = Form("default"),
    team_id: str = Form(""),
    current_user: User = Depends(get_current_user),
):
    """同步上传（单个小文件直接处理，多文件自动转异步）"""
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    file_paths = []
    for file in files:
        try:
            fp = await save_uploaded_file_fastapi(file)
            file_paths.append(fp)
        except Exception as exc:
            pass

    if not file_paths:
        raise HTTPException(status_code=500, detail="文件保存失败")

    total_size = sum(os.path.getsize(fp) for fp in file_paths)
    use_async = len(file_paths) > 2 or total_size > 2 * 1024 * 1024

    if use_async:
        task = task_manager.create_task("document_batch", total=len(file_paths))
        asyncio.create_task(process_document_batch(task, file_paths, current_user.id, kb_id=kb_id, team_id=team_id if team_id else None))
        return {"status": "accepted", "task_id": task.id, "total": len(file_paths), "success_count": 0, "errors": [], "async": True}

    from core.document_parser import DocumentParser
    parser = DocumentParser()
    kb = get_kb(current_user.id, kb_id, team_id=team_id if team_id else None)
    success_count = 0
    errors = []

    for fp in file_paths:
        try:
            parsed = await asyncio.to_thread(parser.parse, fp)
            await asyncio.to_thread(kb.add_document, parsed)
            success_count += 1
        except Exception as exc:
            errors.append(f"{fp}: {exc}")

    return {
        "status": "success",
        "success_count": success_count,
        "total": len(file_paths),
        "errors": errors,
    }


@router.post("/documents/upload-async")
async def upload_documents_async(
    files: list[UploadFile] = File(...),
    kb_id: str = Form("default"),
    team_id: str = Form(""),
    current_user: User = Depends(get_current_user),
):
    """异步上传（大量文件后台处理，返回 task_id 轮询进度）"""
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    file_paths = []
    for file in files:
        try:
            fp = await save_uploaded_file_fastapi(file)
            file_paths.append(fp)
        except Exception:
            pass

    if not file_paths:
        raise HTTPException(status_code=500, detail="文件保存失败")

    task = task_manager.create_task("document_batch", total=len(file_paths))
    asyncio.create_task(process_document_batch(task, file_paths, current_user.id, kb_id=kb_id, team_id=team_id if team_id else None))

    return {"status": "accepted", "task_id": task.id, "total": len(file_paths)}
