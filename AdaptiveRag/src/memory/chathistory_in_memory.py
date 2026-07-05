"""
In-memory chat history store used as a fallback when MongoDB is unavailable.
Not persistent across process restarts -- intended for local dev / testing.
"""
from collections import defaultdict
from typing import Dict, List

from src.core.logger import get_logger

logger = get_logger(__name__)

_HISTORY: Dict[str, List[dict]] = defaultdict(list)


class InMemoryChatHistory:
    async def add_message(self, session_id: str, role: str, content: str) -> None:
        _HISTORY[session_id].append({"role": role, "content": content})

    async def get_history(self, session_id: str) -> List[dict]:
        return _HISTORY.get(session_id, [])

    async def clear(self, session_id: str) -> None:
        _HISTORY.pop(session_id, None)
