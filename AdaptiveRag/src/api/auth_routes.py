"""
Authentication endpoints: register and login.
"""
from fastapi import APIRouter, HTTPException

from src.auth.service import authenticate_user, register_user
from src.models.user import UserCreate, UserLogin
from src.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(user: UserCreate):
    success, message = await register_user(user.username, user.password)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"status": True, "message": message}


@router.post("/login")
async def login(user: UserLogin):
    success, message = await authenticate_user(user.username, user.password)
    if not success:
        raise HTTPException(status_code=401, detail=message)
    return {"status": True, "message": message}
