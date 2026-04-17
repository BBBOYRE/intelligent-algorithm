from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uuid

from server.database import get_db
from server.auth.security import get_current_user
from server.models.user import User
from server.models.knowledge_base_model import KnowledgeBaseModel
from server.dependencies import get_kb, reset_kb

router = APIRouter()


class KBCreateRequest(BaseModel):
    name: str
    description: str = ""


class KBResponse(BaseModel):
    id: str
    name: str
    collection_name: str
    description: str
    total_chunks: int = 0
    documents: list = []

    class Config:
        from_attributes = True


@router.get("/kb/list")
async def list_knowledge_bases(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    kbs = db.query(KnowledgeBaseModel).filter(KnowledgeBaseModel.user_id == current_user.id).all()
    result = []
    for kb_model in kbs:
        try:
            kb = get_kb(current_user.id, kb_model.id)
            stats = kb.get_stats()
            doc_list = [
                {"file_name": d.get("file_name", "unknown"), "format": d.get("metadata", {}).get("format", "")}
                for d in kb.all_parsed_docs
            ]
            result.append({
                "id": kb_model.id,
                "name": kb_model.name,
                "collection_name": kb_model.collection_name,
                "description": kb_model.description,
                "total_chunks": stats.get("total_chunks", 0),
                "documents": doc_list,
            })
        except Exception:
            result.append({
                "id": kb_model.id,
                "name": kb_model.name,
                "collection_name": kb_model.collection_name,
                "description": kb_model.description,
                "total_chunks": 0,
                "documents": [],
            })
    return {"knowledge_bases": result}


@router.post("/kb/create")
async def create_knowledge_base(
    data: KBCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    kb_id = str(uuid.uuid4())
    collection_name = f"kb_{current_user.id}_{kb_id}"
    kb_model = KnowledgeBaseModel(
        id=kb_id,
        user_id=current_user.id,
        name=data.name,
        collection_name=collection_name,
        description=data.description,
    )
    db.add(kb_model)
    db.commit()
    db.refresh(kb_model)
    return {"status": "success", "id": kb_model.id, "name": kb_model.name}


@router.delete("/kb/{kb_id}")
async def delete_knowledge_base(
    kb_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    kb_model = db.query(KnowledgeBaseModel).filter(
        KnowledgeBaseModel.id == kb_id,
        KnowledgeBaseModel.user_id == current_user.id,
    ).first()
    if not kb_model:
        raise HTTPException(status_code=404, detail="知识库不存在")
    try:
        kb = get_kb(current_user.id, kb_id)
        kb.collection.delete(where={})
        kb.all_parsed_docs.clear()
        if kb.docs_storage_file.exists():
            kb.docs_storage_file.write_text("[]", encoding="utf-8")
        reset_kb(current_user.id, kb_id)
    except Exception:
        pass
    db.delete(kb_model)
    db.commit()
    return {"status": "success", "message": f"知识库 '{kb_model.name}' 已删除"}


@router.get("/kb/documents")
async def list_kb_documents(
    kb_id: str = "default",
    query: str = "",
    file_format: str = "",
    current_user: User = Depends(get_current_user),
):
    try:
        kb = get_kb(current_user.id, kb_id)
        docs = kb.search_documents(query=query, file_format=file_format)
        return {"documents": docs}
    except Exception as exc:
        return {"documents": [], "error": str(exc)}


@router.delete("/kb/documents/{file_name}")
async def delete_kb_document(
    file_name: str,
    kb_id: str = "default",
    current_user: User = Depends(get_current_user),
):
    try:
        kb = get_kb(current_user.id, kb_id)
        removed = kb.remove_document(file_name)
        if removed:
            return {"status": "success", "message": f"文档 '{file_name}' 已删除"}
        else:
            raise HTTPException(status_code=404, detail="文档不存在")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/kb/stats")
async def get_kb_stats(
    kb_id: str = "default",
    current_user: User = Depends(get_current_user),
):
    try:
        kb = get_kb(current_user.id, kb_id)
        stats = kb.get_stats()
        doc_list = [
            {"file_name": d.get("file_name", "unknown"), "format": d.get("metadata", {}).get("format", "")}
            for d in kb.all_parsed_docs
        ]
        return {**stats, "documents": doc_list}
    except Exception as exc:
        return {"total_chunks": 0, "documents": [], "error": str(exc)}


@router.delete("/kb/clear")
async def clear_kb(
    kb_id: str = "default",
    current_user: User = Depends(get_current_user),
):
    try:
        kb = get_kb(current_user.id, kb_id)
        kb.collection.delete(where={})
        kb.all_parsed_docs.clear()
        kb.docs_storage_file.write_text("[]", encoding="utf-8")
        reset_kb(current_user.id, kb_id)
        return {"status": "success", "message": "知识库已清空"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
