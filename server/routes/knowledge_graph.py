from fastapi import APIRouter, Depends, HTTPException
from server.auth.security import get_current_user
from server.models.user import User
from server.dependencies import get_kb

router = APIRouter()


@router.get("/knowledge-graph")
async def get_knowledge_graph(
    kb_id: str = "default",
    current_user: User = Depends(get_current_user),
):
    kb = get_kb(current_user.id, kb_id)
    if kb.collection.count() == 0:
        return {"nodes": [], "edges": [], "message": "知识库为空，请先上传文档"}
    try:
        from core.knowledge_graph import KnowledgeGraphBuilder
        builder = KnowledgeGraphBuilder(kb)
        result = builder.build_graph()
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"图谱生成失败: {str(exc)}")
