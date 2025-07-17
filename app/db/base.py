import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from ..core.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,  # Log SQL queries in debug mode
    future=True,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,  # Validate connections before use
    pool_recycle=3600,  # Recycle connections after 1 hour
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.

    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            logger.debug("Created new database session")
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
            logger.debug("Closed database session")


async def create_tables():
    """Create all database tables."""
    async with engine.begin() as conn:
        logger.info("Creating database tables...")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")


async def drop_tables():
    """Drop all database tables."""
    async with engine.begin() as conn:
        logger.warning("Dropping all database tables...")
        await conn.run_sync(Base.metadata.drop_all)
        logger.warning("All database tables dropped")


async def get_engine():
    """Get database engine."""
    return engine


async def close_db():
    """Close database engine."""
    await engine.dispose()
    logger.info("Database engine closed")
