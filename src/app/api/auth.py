"""Authentication API routes."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .deps import get_current_user
from ..db.session import get_db
from ..models import User
from ..schemas import AccessToken, RefreshRequest, TokenPair, UserCreate, UserLogin, UserRead
from ..security import (
    TokenError,
    TokenExpiredError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def signup(user_in: UserCreate, db: Session = Depends(get_db)) -> User:
    """Create a new user with the provided credentials."""

    existing = db.scalar(select(User).where(User.email == user_in.email))
    if existing is not None:
        logger.error("Signup failed: email already registered (%s)", user_in.email)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    user = User(
        email=user_in.email,
        password_hash=hash_password(user_in.password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info("User created: %s", user.email)
    return user


@router.post("/login", response_model=TokenPair)
def login(credentials: UserLogin, db: Session = Depends(get_db)) -> TokenPair:
    """Authenticate a user and return access/refresh tokens."""

    user = db.scalar(select(User).where(User.email == credentials.email))
    if user is None:
        logger.error("Login failed: unknown email %s", credentials.email)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not user.is_active:
        logger.error("Login failed: inactive user %s", credentials.email)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")

    if not verify_password(credentials.password, user.password_hash):
        logger.error("Login failed: bad password for %s", credentials.email)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    logger.info("Login succeeded for %s", user.email)
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    """Return the authenticated user."""

    return current_user


@router.post("/refresh", response_model=AccessToken)
def refresh_token(request: RefreshRequest) -> AccessToken:
    """Generate a new access token from a refresh token."""

    try:
        payload = decode_token(request.refresh_token)
    except TokenExpiredError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired") from exc
    except TokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc

    if payload.type != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    try:
        subject = int(payload.sub)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject") from exc

    access_token = create_access_token(subject)
    return AccessToken(access_token=access_token)


__all__ = ["router"]
