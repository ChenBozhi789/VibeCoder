from typing import Dict, Any, List, Optional
import threading
import uuid
from datetime import datetime, timezone

from backend.db.connection import get_sync_database

class SessionManager:
    """
    会话管理器（MongoDB 版本）
    用于管理聊天历史记录。
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()

    @property
    def _collection(self):
        db = get_sync_database()
        return db["sessions"]

    def create_session(self, initial_message: str = "New Chat") -> Dict[str, Any]:
        """
        创建一个新对话会话。
        用第一条消息的前 20 个字符作为标题。
        """
        with self._lock:
            session_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            title = initial_message[:20] + "..." if len(initial_message) > 20 else initial_message
            
            doc: Dict[str, Any] = {
                "session_id": session_id,
                "title": title,
                "created_at": now,
                "updated_at": now,
                "messages": []
            }
            self._collection.insert_one(doc)
            
            # 返回时去掉 _id，防止 JSON 序列化错误
            doc.pop("_id", None)
            return doc

    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """
        获取所有会话的摘要列表（不包含完整的 messages 数组，按 updated_at 倒序）。
        """
        cursor = self._collection.find(
            {}, 
            {"_id": 0, "session_id": 1, "title": 1, "updated_at": 1}
        ).sort("updated_at", -1)
        return list(cursor)

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取单个会话的完整内容（包含 messages）。
        """
        doc = self._collection.find_one({"session_id": session_id}, {"_id": 0})
        return doc

    def add_message(self, session_id: str, message: Dict[str, Any]) -> bool:
        """
        向指定会话追加一条新消息。
        如果会话存在并更新成功，返回 True。
        """
        with self._lock:
            # 确保消息有时间戳
            if "timestamp" not in message:
                message["timestamp"] = datetime.now(timezone.utc).isoformat()
                
            result = self._collection.update_one(
                {"session_id": session_id},
                {
                    "$push": {"messages": message},
                    "$set": {"updated_at": datetime.now(timezone.utc)}
                }
            )
            return result.modified_count > 0

    def delete_session(self, session_id: str) -> bool:
        """
        删除指定的会话。
        """
        with self._lock:
            result = self._collection.delete_one({"session_id": session_id})
            return result.deleted_count > 0

session_manager = SessionManager()
