import os
import sys
import shutil
import subprocess
import uuid
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from config import Config

router = APIRouter()


class OpenFileRequest(BaseModel):
    path: str


@router.post("/files/open-local")
async def open_local_file(req: OpenFileRequest):
    if not req.path or not os.path.exists(req.path):
        raise HTTPException(status_code=404, detail="File not found")
    try:
        if sys.platform == "win32":
            os.startfile(req.path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", req.path])
        else:
            subprocess.Popen(["xdg-open", req.path])
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cannot open file: {e}")


@router.get("/files/avatar/{filename}")
async def get_avatar(filename: str):
    avatar_dir = os.path.join(Config.UPLOAD_DIR, "avatars")
    filepath = os.path.join(avatar_dir, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Avatar not found")
    return FileResponse(filepath)


@router.get("/files/preview")
async def preview_file(path: str = Query(...)):
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    ext = os.path.splitext(path)[1].lower()
    if ext in (".txt", ".md", ".csv", ".json", ".log"):
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(100000)
        return {"type": "text", "content": content, "filename": os.path.basename(path)}
    try:
        from core.document_parser import DocumentParser
        parser = DocumentParser()
        parsed = parser.parse(path)
        text = parsed.get("text") or parsed.get("raw_text") or "\n".join(parsed.get("chunks", []))
        return {"type": "parsed", "content": text[:100000], "filename": os.path.basename(path)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot preview: {e}")


@router.get("/files/download")
async def download_file(path: str, format: str = Query(None)):
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")

    if format:
        from utils.export_utils import convert_file
        try:
            data, filename = convert_file(path, format)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        media = "text/plain; charset=utf-8"
        if filename.endswith(".csv"):
            media = "text/csv; charset=utf-8"
        elif filename.endswith(".json"):
            media = "application/json; charset=utf-8"
        elif filename.endswith(".md"):
            media = "text/markdown; charset=utf-8"
        return Response(content=data, media_type=media, headers={"Content-Disposition": f'attachment; filename="{filename}"'})

    filename = os.path.basename(path)
    return FileResponse(
        path=path,
        filename=filename,
        media_type="application/octet-stream"
    )


@router.post("/files/save-as")
def save_file_as(path: str = Query(...)):
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        import webview
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Desktop bridge unavailable: {e}")

    windows = webview.windows
    if not windows:
        raise HTTPException(status_code=400, detail="No desktop window available")

    src = Path(path)
    
    try:
        dialog_type = webview.FileDialog.SAVE
    except AttributeError:
        dialog_type = getattr(webview, "SAVE_DIALOG", 10)
        
    try:
        # 调试信息打印
        print(f"Trying to open save dialog for src {src.name} ...")
        save_path = windows[0].create_file_dialog(
            dialog_type,
            save_filename=src.name,
        )
        print(f"Dialog result: {save_path}")
    except Exception as e:
        print("Create file dialog error:", e)
        return {"status": "error", "error": str(e)}

    if not save_path:
        return {"status": "cancelled"}

    if isinstance(save_path, (list, tuple)):
        target = Path(save_path[0])
    else:
        target = Path(str(save_path))

    # Append original file extension if user forgot
    if not target.suffix and src.suffix:
        target = target.with_suffix(src.suffix)

    target.parent.mkdir(parents=True, exist_ok=True)
    import shutil
    shutil.copyfile(src, target)
    return {"status": "success", "saved_to": str(target)}


@router.post("/files/save-temp")
async def save_temp_file(file: UploadFile = File(...)):
    temp_dir = os.path.join(Config.OUTPUT_DIR, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    ext = os.path.splitext(file.filename or "")[1] or ".bin"
    fname = f"{uuid.uuid4().hex[:8]}_{file.filename or 'file'}"
    fpath = os.path.join(temp_dir, fname)
    content = await file.read()
    with open(fpath, "wb") as f:
        f.write(content)
    return {"path": fpath}
