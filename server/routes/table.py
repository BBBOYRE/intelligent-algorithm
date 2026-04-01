from fastapi import APIRouter, UploadFile, File, HTTPException
from utils.file_utils import build_output_path, save_uploaded_file_fastapi

router = APIRouter()

@router.post("/table/fill")
async def fill_table_endpoint(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="未上传模板文件")
        
    try:
        template_path = await save_uploaded_file_fastapi(file)
        
        # build output path based on uploaded filename
        filename = getattr(file, "filename", "template.bin")
        output_path = build_output_path(filename)
        
        from core.knowledge_base import KnowledgeBase
        from core.table_filler import TableFiller

        filler = TableFiller(KnowledgeBase())
        result = filler.fill_template(template_path, output_path)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
