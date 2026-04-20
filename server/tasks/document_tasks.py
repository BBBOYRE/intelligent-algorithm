from __future__ import annotations
import asyncio
from pathlib import Path

from server.tasks.task_manager import Task


async def process_document_batch(
    task: Task,
    file_paths: list[str],
    user_id: str,
    kb_id: str = "default",
    team_id: str = None,
):
    """后台批量处理文档：解析 + 入库"""
    from core.document_parser import DocumentParser
    from server.dependencies import get_kb

    task.status = "running"
    task.total = len(file_paths)
    parser = DocumentParser()
    kb = get_kb(user_id, kb_id, team_id=team_id)

    for i, fp in enumerate(file_paths):
        try:
            parsed = parser.parse(fp)
            kb.add_document(parsed)
            task.completed_count += 1
        except Exception as exc:
            task.errors.append(f"{Path(fp).name}: {exc}")
        task.progress = (i + 1) / task.total
        # 让出事件循环，允许其他请求处理
        await asyncio.sleep(0)

    task.status = "completed" if not task.errors else ("completed" if task.completed_count > 0 else "failed")
    task.result = {
        "success_count": task.completed_count,
        "total": task.total,
        "errors": task.errors,
    }
