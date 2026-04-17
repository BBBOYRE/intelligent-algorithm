from __future__ import annotations
import asyncio
import uuid
from datetime import datetime
from typing import Any


class Task:
    def __init__(self, task_id: str, task_type: str, total: int = 0):
        self.id = task_id
        self.type = task_type
        self.status = "pending"  # pending / running / completed / failed
        self.progress = 0.0
        self.total = total
        self.completed_count = 0
        self.errors: list[str] = []
        self.result: Any = None
        self.created_at = datetime.utcnow().isoformat()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "status": self.status,
            "progress": round(self.progress, 2),
            "total": self.total,
            "completed_count": self.completed_count,
            "errors": self.errors,
            "result": self.result,
            "created_at": self.created_at,
        }


class TaskManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tasks: dict[str, Task] = {}
        return cls._instance

    def create_task(self, task_type: str, total: int = 0) -> Task:
        task_id = str(uuid.uuid4())[:8]
        task = Task(task_id, task_type, total)
        self._tasks[task_id] = task
        return task

    def get_task(self, task_id: str) -> Task | None:
        return self._tasks.get(task_id)

    def list_tasks(self, limit: int = 20) -> list[dict]:
        tasks = sorted(self._tasks.values(), key=lambda t: t.created_at, reverse=True)
        return [t.to_dict() for t in tasks[:limit]]

    def cleanup_old(self, max_tasks: int = 50):
        if len(self._tasks) > max_tasks:
            sorted_tasks = sorted(self._tasks.values(), key=lambda t: t.created_at)
            for t in sorted_tasks[:len(self._tasks) - max_tasks]:
                self._tasks.pop(t.id, None)


task_manager = TaskManager()
