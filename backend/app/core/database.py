"""Asynchronous Database Session and Engine setup with resilient failure handling."""

import logging
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

logger = logging.getLogger(__name__)

# Async SQLAlchemy 2.0 Engine with connection pool
engine = create_async_engine(
    settings.async_database_url,
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True
)

# Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy 2.0 models."""
    pass


async def get_db() -> AsyncGenerator[Optional[AsyncSession], None]:
    """FastAPI dependency that yields an asynchronous database session with graceful fallback."""
    session: Optional[AsyncSession] = None
    try:
        session = AsyncSessionLocal()
        yield session
        try:
            await session.commit()
        except Exception:
            pass
    except Exception as e:
        if session:
            try:
                await session.rollback()
            except Exception:
                pass
        yield None
    finally:
        if session:
            try:
                await session.close()
            except Exception:
                pass
