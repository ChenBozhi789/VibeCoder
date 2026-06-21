from typing import Dict, Any, List, Optional
import uuid
from backend.db.connection import get_sync_database
from pymongo.database import Database

class TaskRepository:
    def __init__(self, db: Optional[Database] = None):
        """
        初始化 TaskRepository。
        如果未提供 db 实例，则自动获取默认的同步数据库连接。
        """
        self.db = db if db is not None else get_sync_database()
        self.collection = self.db["tasks"]
    
    def create_task(self, task_id: str, status: str, progress: int, logs: List[str], result: Any = None) -> None:
        """
        创建一个新任务文档。
        """
        task_doc = {
            "task_id": task_id,
            "status": status,
            "progress": progress,
            "logs": logs,
            "result": result
        }
        self.collection.insert_one(task_doc)

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        根据 task_id 获取任务文档。
        """
        doc = self.collection.find_one({"task_id": task_id}, {"_id": 0})
        return doc

    def update_task(self, task_id: str, updates: Dict[str, Any]) -> None:
        """
        更新任务文档。updates 是要更新的字段字典（如 {"status": "running"}）。
        """
        if not updates:
            return
        
        # 处理 logs 追加逻辑：如果 updates 里有 log 字符串，则追加到 logs 数组
        # 注意：这里为了兼容 TaskManager.update_task 的语义，我们需要特殊处理
        # 但 TaskRepository 应该尽量保持原子性。
        # 更好的做法是在 TaskManager 里组装好 update 操作。
        # 但为了简单，这里假设 TaskManager 传进来的是 $set 或 $push 的操作指令，或者我们在这里封装。
        
        # 鉴于 MongoDB 的灵活性，我们让调用者传入 MongoDB 的 update 操作符会更强大，
        # 但为了解耦，我们还是定义清晰的参数。
        
        # 这里我们假设 updates 是要 $set 的字段。
        # 如果有 logs 需要追加，调用者应该使用 append_log 方法，或者我们在 updates 里约定。
        
        # 为了兼容现有逻辑，我们只处理 $set。日志追加单独处理或由调用者合并。
        # 实际上 TaskManager update_task 逻辑是：status?, progress?, log?, result?
        
        mongo_update = {}
        set_fields = {}
        push_fields = {}
        
        for k, v in updates.items():
            if k == "log": # 特殊处理单条日志追加
                push_fields["logs"] = v
            elif k == "logs": # 直接覆盖 logs (不常用，但支持)
                set_fields["logs"] = v
            else:
                set_fields[k] = v
                
        if set_fields:
            mongo_update["$set"] = set_fields
        if push_fields:
            mongo_update["$push"] = push_fields
            
        if mongo_update:
            self.collection.update_one({"task_id": task_id}, mongo_update)

    def get_all_tasks(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有任务，返回格式与 TaskManager 兼容：{ "task_id": { ... } }
        """
        cursor = self.collection.find({}, {"_id": 0})
        tasks = {}
        for doc in cursor:
            tasks[doc["task_id"]] = doc
        return tasks

    def get_all_task_ids(self) -> List[str]:
        """
        获取所有 task_id 列表。
        """
        cursor = self.collection.find({}, {"task_id": 1, "_id": 0})
        return [doc["task_id"] for doc in cursor]
