from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.db.session import get_session
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, PasswordResetRequest
from app.schemas.user import UserRead

router = APIRouter()


# PUBLIC_INTERFACE
@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Creates a new user account with a unique email and username.",
)
async def register(payload: RegisterRequest, session: AsyncSession = Depends(get_session)) -> UserRead:
    """
    Register a new user.

    Args:
        payload: RegisterRequest containing username, email, and password.
        session: Async database session.

    Returns:
        UserRead: Newly created user data (without password hash).

    Raises:
        HTTPException: 400 if email already exists.
    """
    existing = await session.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(username=payload.username, email=payload.email, password_hash=get_password_hash(payload.password))
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return UserRead.model_validate(user)


# PUBLIC_INTERFACE
@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate user and return JWT",
    description="Authenticates the user and returns an access token.",
)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_session)) -> TokenResponse:
    """
    Authenticate user and return JWT.

    Args:
        payload: LoginRequest with email and password.
        session: Async database session.

    Returns:
        TokenResponse: JWT access token and expiry in seconds.

    Raises:
        HTTPException: 401 if invalid credentials.
    """
    result = await session.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token({"sub": str(user.id)}, expires_delta=access_token_expires)
    return TokenResponse(access_token=token, expires_in=int(access_token_expires.total_seconds()))


# PUBLIC_INTERFACE
@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    summary="Initiate password reset",
    description="Dummy password reset endpoint. In production, send a reset email.",
)
async def reset_password(payload: PasswordResetRequest) -> dict:
    """
    Initiate password reset flow (placeholder).

    Args:
        payload: PasswordResetRequest containing user email.

    Returns:
        dict: Confirmation message.
    """
    # Placeholder: In real implementation, generate token and send email.
    return {"message": f"If an account exists for {payload.email}, a password reset link will be sent."}


# PUBLIC_INTERFACE
@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Invalidate user session",
    description="Stateless JWTs cannot be invalidated server-side without a blocklist. This endpoint returns 204.",
)
async def logout() -> None:
    """
    Logout endpoint placeholder for stateless JWT.

    Returns:
        None with 204 status.
    """
    return None
