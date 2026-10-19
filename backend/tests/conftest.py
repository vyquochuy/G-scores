from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.cache import cache_manager
from app.core.database import async_engine
from app.main import app


@pytest.fixture(autouse=True)
async def dispose_engine() -> AsyncGenerator[None, None]:
    """Tu dong giai phong pool ket noi cua async_engine va cache_manager sau moi test."""
    yield
    await cache_manager.close()
    await async_engine.dispose()


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Fixture cung cap AsyncClient de thuc hien cac kiem thu HTTP endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
