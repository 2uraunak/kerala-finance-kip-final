"""
Authentication router — login, logout, token refresh.
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models.user import User
from middleware.auth import verify_password, create_access_token

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


@router.post("/login", response_model=TokenResponse, summary="Login and get JWT token")
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Authenticate with username/password, receive a JWT bearer token.
    Use this token in the Authorization: Bearer <token> header for all other endpoints.
    """
    result = await db.execute(select(User).where(User.username == payload.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    user.last_login = datetime.utcnow()
    await db.commit()

    token = create_access_token({"sub": user.username, "role": user.role})
    return TokenResponse(access_token=token, user=user.to_dict())


@router.get("/me", summary="Get current user profile")
async def me(db: AsyncSession = Depends(get_db), current_user: User = Depends(lambda: None)):
    """Returns the currently authenticated user's profile."""
    from middleware.auth import get_current_user
    return {"user": current_user.to_dict() if current_user else None}
