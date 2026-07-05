"""
MongoDB client initialization using Motor (async driver).
Falls back gracefully if MongoDB is unreachable -- callers should catch
exceptions and use the in-memory chat history fallback in that case.
"""
import time

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from src.config.settings import settings
from src.core.logger import get_logger

logger = get_logger(__name__)

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None

# Keep local-dev startup/requests snappy: fail fast instead of the ~20-30s
# PyMongo default, and cache the result briefly so every request doesn't
# re-pay the connection-timeout cost while Mongo is down.
_SERVER_SELECTION_TIMEOUT_MS = 2000
_PING_CACHE_TTL_SECONDS = 10
_last_ping_result: bool | None = None
_last_ping_time: float = 0.0


def get_mongo_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        logger.info("Initializing MongoDB client at %s", settings.MONGODB_URL)
        _client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=_SERVER_SELECTION_TIMEOUT_MS,
            connectTimeoutMS=_SERVER_SELECTION_TIMEOUT_MS,
            socketTimeoutMS=_SERVER_SELECTION_TIMEOUT_MS,
        )
    return _client


def get_database() -> AsyncIOMotorDatabase:
    global _db
    if _db is None:
        _db = get_mongo_client()[settings.MONGODB_DB_NAME]
    return _db


async def ping() -> bool:
    """
    Check MongoDB connectivity, failing fast (~2s) rather than the PyMongo
    default (~20-30s). Result is cached briefly so callers hitting this on
    every request don't repeatedly eat the timeout while Mongo is down.
    """
    global _last_ping_result, _last_ping_time

    now = time.monotonic()
    if _last_ping_result is not None and (now - _last_ping_time) < _PING_CACHE_TTL_SECONDS:
        return _last_ping_result

    try:
        await get_mongo_client().admin.command("ping")
        _last_ping_result = True
    except Exception as exc:  # noqa: BLE001
        logger.warning("MongoDB ping failed: %s", exc)
        _last_ping_result = False

    _last_ping_time = now
    return _last_ping_result
