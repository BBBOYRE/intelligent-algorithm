import os
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, Response

router = APIRouter()


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
