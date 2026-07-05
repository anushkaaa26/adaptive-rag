"""
MongoDB-backed chat history with automatic fallback to in-memory storage
if MongoDB is unreachable.
"""
from datetime import datetime, timezone
from typing import List

from src.db.mongo_client import get_database, ping
from src.memory.chathistory_in_memory import InMemoryChatHistory
from src.core.logger import get_logger

logger = get_logger(__name__)

_fallback = InMemoryChatHistory()


class MongoChatHistory:
    """Persists chat messages in a MongoDB collection, per session_id."""

    def __init__(self, collection_name: str = "chat_history"):
        self.collection_name = collection_name
        self._use_fallback = False

    async def _get_collection(self):
        if not await ping():
            if not self._use_fallback:
                logger.warning("MongoDB unavailable -- falling back to in-memory chat history.")
                self._use_fallback = True
            return None
        self._use_fallback = False
        return get_database()[self.collection_name]

    async def add_message(self, session_id: str, role: str, content: str) -> None:
        collection = await self._get_collection()
        if collection is None:
            await _fallback.add_message(session_id, role, content)
            return
        await collection.insert_one(
            {
                "session_id": session_id,
                "role": role,
                "content": content,
                "timestamp": datetime.now(timezone.utc),
            }
        )

    async def get_history(self, session_id: str) -> List[dict]:
        collection = await self._get_collection()
        if collection is None:
            return await _fallback.get_history(session_id)
        cursor = collection.find({"session_id": session_id}).sort("timestamp", 1)
        return [{"role": doc["role"], "content": doc["content"]} async for doc in cursor]

    async def clear(self, session_id: str) -> None:
        collection = await self._get_collection()
        if collection is None:
            await _fallback.clear(session_id)
            return
        await collection.delete_many({"session_id": session_id})
