import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from utils.file_utils import save_uploaded_file_fastapi

router = APIRouter()

@router.post("/documents/upload")
async def upload_documents(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded or parameter 'files' is missing")

    from core.document_parser import DocumentParser
    from core.knowledge_base import KnowledgeBase

    parser = DocumentParser()
    kb = KnowledgeBase()
    success_count = 0
    errors = []

    for file in files:
        try:
            # save file locally first
            file_path = await save_uploaded_file_fastapi(file)
            parsed = parser.parse(file_path)
            kb.add_document(parsed)
            success_count += 1
        except Exception as exc:
            errors.append(f"{file.filename}: {exc}")

    if success_count == 0 and errors:
        raise HTTPException(status_code=500, detail=f"上传失败: {', '.join(errors)}")

    return {
        "status": "success",
        "success_count": success_count,
        "total": len(files),
        "errors": errors
    }
