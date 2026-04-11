from __future__ import annotations

from core.knowledge_base import KnowledgeBase


def retrieve_context(kb: KnowledgeBase, query: str, top_k: int = 5) -> str:
    """Retrieve top-k chunks and merge into a readable context block."""
    hits = kb.search(query=query, top_k=top_k)
    if not hits:
        return ""
    return "\n\n---\n\n".join(
        f"[来源: {item['metadata'].get('source', 'unknown')}]\n{item['text']}"
        for item in hits
    )
