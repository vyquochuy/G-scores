import os

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Cau hinh AsyncEngine phu hop ca moi truong local va serverless/PgBouncer:
# 1. statement_cache_size: 0 vo hieu hoa statement caching cua asyncpg,
#    ngan ngua loi DuplicatePreparedStatementError / InvalidSQLStatementNameError
#    khi su dung PgBouncer transaction pooling (Supabase, Neon, v.v.).
# 2. NullPool tren Vercel giup dong connection ngay sau request thay vi giu pool chet khi freeze.
is_serverless = os.getenv("VERCEL") == "1"

engine_kwargs: dict = {
    "echo": False,
    "future": True,
    "pool_pre_ping": True,
    "connect_args": {
        "statement_cache_size": 0,
    },
}

if is_serverless:
    engine_kwargs["poolclass"] = NullPool

async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URI,
    **engine_kwargs,
)

async_session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db_session():
    """FastAPI dependency cung cap async database session cho moi request."""
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise

