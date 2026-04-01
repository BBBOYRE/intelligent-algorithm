import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()

@router.get("/files/download")
async def download_file(path: str):
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    
    filename = os.path.basename(path)
    return FileResponse(
        path=path,
        filename=filename,
        media_type="application/octet-stream"
    )
