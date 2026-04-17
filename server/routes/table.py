import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from utils.file_utils import build_output_path, save_uploaded_file_fastapi
from server.auth.security import get_current_user
from server.models.user import User
from server.dependencies import get_kb

router = APIRouter()

_filler_cache: dict[str, object] = {}


def _get_filler(user_id: str):
    if user_id not in _filler_cache:
        from core.table_filler import TableFiller
        _filler_cache[user_id] = TableFiller(get_kb(user_id))
    return _filler_cache[user_id]


@router.post("/table/preview")
async def preview_table_fill(
    file: UploadFile = File(...),
    custom_requirements: str = Form(""),
    fill_precision: str = Form("fine"),
    current_user: User = Depends(get_current_user),
):
    if not file:
        raise HTTPException(status_code=400, detail="未上传模板文件")
    try:
        template_path = await save_uploaded_file_fastapi(file)
        filler = _get_filler(current_user.id)
        result = filler.preview_fill(template_path, requirements=custom_requirements, precision=fill_precision)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/table/fill")
async def fill_table_endpoint(
    file: UploadFile = File(...),
    custom_requirements: str = Form(""),
    fill_precision: str = Form("fine"),
    current_user: User = Depends(get_current_user),
):
    if not file:
        raise HTTPException(status_code=400, detail="未上传模板文件")
    try:
        template_path = await save_uploaded_file_fastapi(file)
        filename = getattr(file, "filename", "template.bin")
        output_path = build_output_path(filename)
        filler = _get_filler(current_user.id)
        result = filler.fill_template(
            template_path,
            output_path,
            requirements=custom_requirements,
            precision=fill_precision,
        )
        if result.get("status") == "success" and os.path.exists(result["output_path"]):
            return result
        else:
            raise HTTPException(status_code=500, detail="填表失败或未能生成有效文件")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
