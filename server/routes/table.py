import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from utils.file_utils import build_output_path, save_uploaded_file_fastapi

router = APIRouter()

@router.post("/table/fill")
async def fill_table_endpoint(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="未上传模板文件")
        
    try:
        template_path = await save_uploaded_file_fastapi(file)
        filename = getattr(file, "filename", "template.bin")
        output_path = build_output_path(filename)
        
        from core.knowledge_base import KnowledgeBase
        from core.table_filler import TableFiller

        filler = TableFiller(KnowledgeBase())
        result = filler.fill_template(template_path, output_path)
        
        # [核心修复] 恢复成返回 JSON，让前端能够正常解析并展示成功动画！
        if result.get("status") == "success" and os.path.exists(result["output_path"]):
            # 直接返回字典，FastAPI 会自动将其转换为前端期待的 JSON 格式
            return result
        else:
            raise HTTPException(status_code=500, detail="填表失败或未能生成有效文件")
            
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))