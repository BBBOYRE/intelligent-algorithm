import os
import time
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from utils.file_utils import build_output_path, save_uploaded_file_fastapi
from server.auth.security import get_current_user
from server.models.user import User
from server.dependencies import get_kb

router = APIRouter()

_filler_cache: dict[str, object] = {}


def _get_filler(user_id: str, kb_id: str = "default", team_id: str = None):
    cache_key = f"{user_id}_{kb_id}_{team_id}"
    if cache_key not in _filler_cache:
        from core.table_filler import TableFiller
        kb = get_kb(user_id, kb_id, team_id=team_id)
        print(f"[TABLE] Creating filler: user={user_id} kb={kb_id} team={team_id} chunks={kb.get_stats().get('total_chunks',0)} docs={len(kb.all_parsed_docs)}", flush=True)
        _filler_cache[cache_key] = TableFiller(kb)
    return _filler_cache[cache_key]


@router.post("/table/preview")
async def preview_table_fill(
    file: UploadFile = File(...),
    custom_requirements: str = Form(""),
    fill_precision: str = Form("fine"),
    kb_id: str = Form("default"),
    team_id: str = Form(""),
    current_user: User = Depends(get_current_user),
):
    if not file:
        raise HTTPException(status_code=400, detail="未上传模板文件")
    t0 = time.time()
    print(f"[TABLE PREVIEW] Start: file={file.filename} kb={kb_id} team={team_id} precision={fill_precision} requirements='{custom_requirements[:50]}'", flush=True)
    try:
        template_path = await save_uploaded_file_fastapi(file)
        print(f"[TABLE PREVIEW] Template saved: {template_path}", flush=True)
        filler = _get_filler(current_user.id, kb_id, team_id if team_id else None)
        result = filler.preview_fill(template_path, requirements=custom_requirements, precision=fill_precision)
        elapsed = time.time() - t0
        tables = result.get("tables", [])
        total_rows = sum(len(t.get("rows", [])) for t in tables)
        print(f"[TABLE PREVIEW] Done in {elapsed:.1f}s: {len(tables)} tables, {total_rows} rows", flush=True)
        return result
    except Exception as exc:
        elapsed = time.time() - t0
        print(f"[TABLE PREVIEW] FAILED in {elapsed:.1f}s: {exc}", flush=True)
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/table/fill")
async def fill_table_endpoint(
    file: UploadFile = File(...),
    custom_requirements: str = Form(""),
    fill_precision: str = Form("fine"),
    kb_id: str = Form("default"),
    team_id: str = Form(""),
    current_user: User = Depends(get_current_user),
):
    if not file:
        raise HTTPException(status_code=400, detail="未上传模板文件")
    t0 = time.time()
    print(f"[TABLE FILL] Start: file={file.filename} kb={kb_id} team={team_id} precision={fill_precision}", flush=True)
    try:
        template_path = await save_uploaded_file_fastapi(file)
        filename = getattr(file, "filename", "template.bin")
        output_path = build_output_path(filename)
        filler = _get_filler(current_user.id, kb_id, team_id if team_id else None)
        result = filler.fill_template(
            template_path,
            output_path,
            requirements=custom_requirements,
            precision=fill_precision,
        )
        elapsed = time.time() - t0
        print(f"[TABLE FILL] Done in {elapsed:.1f}s: filled={result.get('filled_cells',0)} output={result.get('output_path','')}", flush=True)
        if result.get("status") == "success" and os.path.exists(result["output_path"]):
            from server.services.webhook_dispatcher import dispatch_event
            await dispatch_event(current_user.id, "table.filled", {"filled_cells": result.get("filled_cells", 0)})
            return result
        else:
            raise HTTPException(status_code=500, detail="填表失败或未能生成有效文件")
    except Exception as exc:
        elapsed = time.time() - t0
        print(f"[TABLE FILL] FAILED in {elapsed:.1f}s: {exc}", flush=True)
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc))
