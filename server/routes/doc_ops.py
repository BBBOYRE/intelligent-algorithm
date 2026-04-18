from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from pydantic import BaseModel
from utils.file_utils import save_uploaded_file_fastapi
from server.auth.security import get_current_user
from server.models.user import User
import shutil
import os

router = APIRouter()


class WriteBackRequest(BaseModel):
    output_path: str
    source_path: str


@router.post("/doc-ops/execute")
async def execute_doc_operation(
    file: UploadFile = File(...),
    instruction: str = Form(...),
    current_user: User = Depends(get_current_user),
):
    if not file:
        raise HTTPException(status_code=400, detail="未上传文档文件")
    if not instruction or not instruction.strip():
        raise HTTPException(status_code=400, detail="操作指令不能为空")
    try:
        file_path = await save_uploaded_file_fastapi(file)
        from core.doc_operator import DocOperator
        operator = DocOperator()
        result = operator.execute(file_path, instruction)
        result["source_path"] = file_path
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/doc-ops/write-back")
async def write_back(
    req: WriteBackRequest,
    current_user: User = Depends(get_current_user),
):
    if not req.output_path or not os.path.exists(req.output_path):
        raise HTTPException(status_code=404, detail="Output file not found")
    if not req.source_path:
        raise HTTPException(status_code=400, detail="Source path is required")
    try:
        shutil.copyfile(req.output_path, req.source_path)
        return {"status": "success", "message": f"已写回到 {os.path.basename(req.source_path)}"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Write back failed: {exc}")


@router.post("/doc-ops/compare")
async def compare_documents(
    file_a: UploadFile = File(...),
    file_b: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    if not file_a or not file_b:
        raise HTTPException(status_code=400, detail="请上传两个文档")
    try:
        path_a = await save_uploaded_file_fastapi(file_a)
        path_b = await save_uploaded_file_fastapi(file_b)
        from core.doc_comparator import DocComparator
        comparator = DocComparator()
        result = comparator.compare(path_a, path_b)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
