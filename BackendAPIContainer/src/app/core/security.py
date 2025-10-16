from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_session
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
oauth2_scheme_optional = HTTPBearer(auto_error=False)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


# PUBLIC_INTERFACE
async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)) -> User:
    """
    Decode the JWT token and return the authenticated user.

    Args:
        token: Bearer token from Authorization header.
        session: Async DB session.

    Returns:
        User: Authenticated user instance.

    Raises:
        HTTPException: 401 if token invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    result = await session.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


# PUBLIC_INTERFACE
async def get_preview_or_current_user(
    session: AsyncSession = Depends(get_session),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(oauth2_scheme_optional)
) -> User:
    """
    Return a stub preview user if PREVIEW_NO_AUTH is enabled, otherwise validate token and return authenticated user.

    This dependency allows unauthenticated access to routes when PREVIEW_NO_AUTH=true,
    enabling easy preview/testing without authentication. In production, PREVIEW_NO_AUTH
    should be set to false to enforce full authentication.

    Args:
        session: Async DB session.
        credentials: Optional Bearer token credentials from Authorization header.

    Returns:
        User: Stub preview user if preview mode enabled, otherwise authenticated user.

    Raises:
        HTTPException: 401 if preview mode disabled and token invalid or user not found.
    """
    if settings.PREVIEW_NO_AUTH:
        # Return a stub user for preview mode
        # Check if a preview user exists in the database, otherwise create a stub in-memory user
        result = await session.execute(select(User).where(User.email == "preview@example.com"))
        preview_user = result.scalar_one_or_none()
        
        if preview_user is None:
            # Create an in-memory stub user (not persisted to DB)
            preview_user = User()
            preview_user.id = 9999
            preview_user.username = "preview_user"
            preview_user.email = "preview@example.com"
            preview_user.password_hash = ""
            preview_user.created_at = datetime.utcnow()
            preview_user.updated_at = datetime.utcnow()
        
        return preview_user
    
    # Normal authentication flow when preview mode is disabled
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    token = credentials.credentials
    return await get_current_user(token=token, session=session)
