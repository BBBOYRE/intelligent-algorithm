from core.knowledge_base import KnowledgeBase

_kb_cache: dict[str, KnowledgeBase] = {}


def get_kb(user_id: str = "default", kb_id: str = "default") -> KnowledgeBase:
    """按 user_id + kb_id 获取隔离的 KnowledgeBase 实例"""
    cache_key = f"{user_id}_{kb_id}"
    if cache_key not in _kb_cache:
        collection_name = f"kb_{user_id}_{kb_id}" if user_id != "default" else "documents"
        _kb_cache[cache_key] = KnowledgeBase(collection_name=collection_name)
    return _kb_cache[cache_key]


def reset_kb(user_id: str = "default", kb_id: str = "default") -> None:
    cache_key = f"{user_id}_{kb_id}"
    _kb_cache.pop(cache_key, None)


def reset_all_kb() -> None:
    _kb_cache.clear()
