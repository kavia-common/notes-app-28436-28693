from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

_engine = None
_async_session_factory: async_sessionmaker | None = None


def init_engine_and_session() -> None:
    """Initialize SQLAlchemy engine and sessionmaker once."""
    global _engine, _async_session_factory
    if _engine is None:
        _engine = create_async_engine(settings.DATABASE_URL, future=True, echo=False)
        _async_session_factory = async_sessionmaker(bind=_engine, expire_on_commit=False, class_=AsyncSession)


# PUBLIC_INTERFACE
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an AsyncSession.

    Yields:
        AsyncSession: A SQLAlchemy async session.
    """
    if _async_session_factory is None:
        init_engine_and_session()
    assert _async_session_factory is not None
    async with _async_session_factory() as session:
        yield session
