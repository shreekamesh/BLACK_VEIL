"""
BLACK VEIL V5 - Authentication Endpoints
User login, registration, token refresh, API key management
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select

from src.backend.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    API_KEY_PREFIX,
)
from src.backend.database.postgres import postgres_db
from src.backend.models.database_models import User, UserSession
from src.backend.utils.crypto import CryptoUtils
from src.backend.utils.validators import Validators
from src.backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["Authentication"])


class LoginRequest(BaseModel):
    """Login request payload"""
    username: str = Field(..., min_length=2, max_length=128)
    password: str = Field(..., min_length=8, max_length=256)


class RegisterRequest(BaseModel):
    """Registration request payload"""
    username: str = Field(..., min_length=2, max_length=128)
    password: str = Field(..., min_length=8, max_length=256)
    email: Optional[str] = Field(None, max_length=255)
    role: str = Field("viewer", pattern="^(viewer|analyst|operator|admin)$")


class TokenResponse(BaseModel):
    """Token response payload"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    role: str
    permissions: list


class RefreshRequest(BaseModel):
    """Token refresh request"""
    refresh_token: str


def create_access_token(user: User) -> str:
    """Create a JWT access token for a user"""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": user.id,
        "username": user.username,
        "role": user.role,
        "permissions": user.permissions or [],
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "type": "access",
    }

    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_refresh_token(user: User) -> str:
    """Create a refresh token"""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": user.id,
        "username": user.username,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "type": "refresh",
    }

    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Authenticate user and return tokens"""
    async with postgres_db.get_session() as session:
        stmt = select(User).where(User.username == request.username)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # Verify password (stored as hash:password format from CryptoUtils)
    if not CryptoUtils.verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # Update last login
    user.last_login = datetime.now(timezone.utc)

    # Generate tokens
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        role=user.role,
        permissions=user.permissions or [],
    )


@router.post("/register")
async def register(request: RegisterRequest):
    """Register a new user account"""
    if len(request.username) < 2:
        raise HTTPException(status_code=422, detail="Username too short")

    if request.email and not Validators.validate_email(request.email):
        raise HTTPException(status_code=422, detail="Invalid email format")

    # Check if username exists
    async with postgres_db.get_session() as session:
        stmt = select(User).where(User.username == request.username)
        result = await session.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Username already exists")

    # Hash password
    password_hash, salt = CryptoUtils.hash_password(request.password)

    # Create user
    user = User(
        username=request.username,
        email=request.email,
        password_hash=password_hash,
        role=request.role,
        permissions={"roles": [request.role]},
    )

    async with postgres_db.get_session() as session:
        session.add(user)

    logger.info("User registered: %s (role: %s)", request.username, request.role)

    return {
        "status": "registered",
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshRequest):
    """Refresh access token using refresh token"""
    try:
        payload = jwt.decode(
            request.refresh_token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    # Get user
    async with postgres_db.get_session() as session:
        stmt = select(User).where(User.id == payload["sub"])
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    # Generate new tokens
    access_token = create_access_token(user)
    new_refresh_token = create_refresh_token(user)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        role=user.role,
        permissions=user.permissions or [],
    )


@router.post("/api-key")
async def generate_api_key():
    """Generate a new API key"""
    api_key = CryptoUtils.generate_api_key()
    return {
        "api_key": api_key,
        "prefix": API_KEY_PREFIX,
        "note": "Save this key securely. It will not be shown again.",
    }
