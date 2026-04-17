import asyncio
import traceback
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from server.auth.security import get_current_user
from server.models.user import User
from server.dependencies import get_kb

router = APIRouter()

_kg_results: dict[str, dict] = {}


class KGRequest(BaseModel):
    file_names: Optional[list[str]] = None


@router.post("/knowledge-graph/generate")
async def generate_knowledge_graph(
    data: KGRequest = KGRequest(),
    kb_id: str = Query("default"),
    current_user: User = Depends(get_current_user),
):
    kb = get_kb(current_user.id, kb_id)
    task_id = f"kg_{current_user.id}_{kb_id}"
    _kg_results[task_id] = {"status": "running"}

    def _blocking_build():
        from core.knowledge_graph import KnowledgeGraphBuilder
        builder = KnowledgeGraphBuilder(kb)
        return builder.build_graph(file_names=data.file_names)

    async def _run():
        try:
            result = await asyncio.to_thread(_blocking_build)
            _kg_results[task_id] = {"status": "done", **result}
        except Exception as exc:
            _kg_results[task_id] = {"status": "error", "detail": str(exc)}

    asyncio.create_task(_run())
    return {"task_id": task_id}


@router.get("/knowledge-graph/result/{task_id}")
async def get_kg_result(
    task_id: str,
    current_user: User = Depends(get_current_user),
):
    result = _kg_results.get(task_id)
    if not result:
        raise HTTPException(status_code=404, detail="任务不存在")
    return result


@router.get("/knowledge-graph/files")
async def list_kg_files(
    kb_id: str = Query("default"),
    current_user: User = Depends(get_current_user),
):
    kb = get_kb(current_user.id, kb_id)
    files = []
    seen = set()
    for doc in kb.all_parsed_docs:
        name = doc.get("file_name", "")
        if name and name not in seen:
            seen.add(name)
            files.append({"name": name, "word_count": doc.get("word_count", 0)})
    return files
