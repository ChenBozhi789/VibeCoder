import os
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import MongoClient
from pymongo.database import Database

_mongo_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None

_sync_client: Optional[MongoClient] = None
_sync_db: Optional[Database] = None


def get_mongo_client() -> AsyncIOMotorClient:
    """
    全局单例 Mongo 异步客户端，用环境变量 MONGODB_URI 连接。
    例如：mongodb://localhost:27017/vibecoder_db
    """
    global _mongo_client, _db
    if _mongo_client is None:
        uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/vibecoder_db")
        _mongo_client = AsyncIOMotorClient(uri)
        # 如果 URI 里带了库名（你现在就是），可以直接用 get_default_database
        _db = _mongo_client.get_default_database()
    return _mongo_client


def get_database() -> AsyncIOMotorDatabase:
    """
    拿到默认的异步数据库对象，在仓储/服务里用。
    """
    global _db
    if _db is None:
        get_mongo_client()
    assert _db is not None
    return _db


def get_sync_client() -> MongoClient:
    """
    全局单例 Mongo 同步客户端，用于后台线程（Thread）中无法使用 await 的场景。
    """
    global _sync_client, _sync_db
    if _sync_client is None:
        uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/vibecoder_db")
        _sync_client = MongoClient(uri)
        _sync_db = _sync_client.get_default_database()
    return _sync_client


def get_sync_database() -> Database:
    """
    拿到默认的同步数据库对象。
    """
    global _sync_db
    if _sync_db is None:
        get_sync_client()
    assert _sync_db is not None
    return _sync_db


async def close_mongo_client() -> None:
    """
    在 FastAPI 关闭时调用，优雅关闭连接。
    """
    global _mongo_client, _sync_client
    if _mongo_client is not None:
        _mongo_client.close()
        _mongo_client = None
    
    if _sync_client is not None:
        _sync_client.close()
        _sync_client = None