# backend/utils/task_manager.py
from typing import Dict, Any
from enum import Enum
import threading
import uuid
from datetime import datetime, timezone

from backend.db.connection import get_sync_database


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskManager:
    """
    任务管理器（MongoDB 版本）

    - 不再使用本地 JSON 文件，而是直接把任务存到 MongoDB 的 tasks 集合。
    - 对外接口保持不变：create_task / update_task / get_task / get_all_tasks / retrieve_task_id。
    """

    def __init__(self) -> None:
        # 这里的锁只保证多线程情况下的基本原子性，实际持久化由 MongoDB 完成。
        self._lock = threading.Lock()

    @property
    def _collection(self):
        db = get_sync_database()
        return db["tasks"]

    def create_task(self) -> str:
        """
        创建一个新任务，并写入 MongoDB。
        """
        with self._lock:
            task_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            doc: Dict[str, Any] = {
                "task_id": task_id,
                "status": TaskStatus.PENDING.value,
                "progress": 0,
                "logs": ["Task created, waiting to start..."],
                "result": None,
                "created_at": now,
                "updated_at": now,
            }
            self._collection.insert_one(doc)
            return task_id

    def update_task(
        self,
        task_id: str,
        status: str | None = None,
        progress: int | None = None,
        log: str | None = None,
        result: Any | None = None,
    ) -> None:
        """
        更新任务的状态/进度/日志/结果。
        """
        update: Dict[str, Any] = {"updated_at": datetime.now(timezone.utc)}
        if status is not None:
            update["status"] = status
        if progress is not None:
            update["progress"] = progress
        if result is not None:
            update["result"] = result

        with self._lock:
            update_doc: Dict[str, Any] = {}
            if update:
                update_doc["$set"] = update
            if log:
                update_doc.setdefault("$push", {})["logs"] = log

            if update_doc:
                self._collection.update_one({"task_id": task_id}, update_doc)

    def get_task(self, task_id: str):
        """
        根据 task_id 获取单个任务，返回 dict（不包含 _id）。
        """
        doc = self._collection.find_one({"task_id": task_id}, {"_id": 0})
        return doc

    def get_all_tasks(self):
        """
        获取所有任务的完整信息
        返回格式: { "task_id": { "status", "progress", "logs", "result", ... } }
        """
        tasks: Dict[str, Dict[str, Any]] = {}
        for doc in self._collection.find({}, {"_id": 0}):
            task_id = doc.get("task_id")
            if task_id:
                # 按原接口约定，将 task_id 作为 key，其余字段作为 value
                tasks[task_id] = {
                    k: v for k, v in doc.items() if k != "task_id"
                }
        return tasks

    def retrieve_task_id(self):
        """
        获取所有 task_id 列表
        """
        ids = []
        for doc in self._collection.find({}, {"task_id": 1, "_id": 0}):
            if "task_id" in doc:
                ids.append(doc["task_id"])
        return ids


task_manager = TaskManager()