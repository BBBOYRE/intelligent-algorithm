from fastapi import APIRouter

router = APIRouter()

@router.get("/kb/stats")
async def get_kb_stats():
    try:
        from core.knowledge_base import KnowledgeBase
        
        kb = KnowledgeBase()
        stats = kb.get_stats()
        return stats
    except Exception as exc:
        return {"total_chunks": 0, "error": str(exc)}
