"""
Authentication service: user registration and login.

Passwords are hashed with bcrypt via passlib. User records are stored in
MongoDB when available, with an in-memory fallback (mirroring the pattern
used for chat history) so the app remains usable without a live database
during local development.
"""
from typing import Dict, Optional

from passlib.context import CryptContext

from src.db.mongo_client import get_database, ping
from src.core.logger import get_logger

logger = get_logger(__name__)

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory fallback store: {username: hashed_password}
_USERS: Dict[str, str] = {}


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return _pwd_context.verify(password, hashed)


async def _get_users_collection():
    if not await ping():
        return None
    return get_database()["users"]


async def register_user(username: str, password: str) -> tuple[bool, str]:
    """Returns (success, message)."""
    username = username.strip().lower()
    hashed = hash_password(password)

    collection = await _get_users_collection()
    if collection is None:
        if username in _USERS:
            return False, "Username already exists."
        _USERS[username] = hashed
        logger.warning("MongoDB unavailable -- registered user '%s' in-memory only.", username)
        return True, "Registered (in-memory fallback -- not persistent)."

    existing = await collection.find_one({"username": username})
    if existing:
        return False, "Username already exists."

    await collection.insert_one({"username": username, "password_hash": hashed})
    return True, "Registered successfully."


async def authenticate_user(username: str, password: str) -> tuple[bool, str]:
    """Returns (success, message)."""
    username = username.strip().lower()

    collection = await _get_users_collection()
    if collection is None:
        hashed = _USERS.get(username)
        if hashed and verify_password(password, hashed):
            return True, "Login successful (in-memory fallback)."
        return False, "Invalid username or password."

    user = await collection.find_one({"username": username})
    if not user or not verify_password(password, user["password_hash"]):
        return False, "Invalid username or password."
    return True, "Login successful."
