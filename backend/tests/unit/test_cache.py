from unittest.mock import AsyncMock, patch

import pytest
from redis.exceptions import ConnectionError, TimeoutError

from app.core.cache import (
    CacheManager,
    get_distribution_cache_key,
    get_top_a_cache_key,
)


def test_cache_key_generators() -> None:
    assert get_distribution_cache_key("toan") == "reports:distribution:v1:toan"
    assert get_distribution_cache_key("TOAN ") == "reports:distribution:v1:toan"
    assert get_distribution_cache_key("") == "reports:distribution:v1:all"
    assert get_top_a_cache_key(10) == "students:top_a:v1:10"
    assert get_top_a_cache_key(5) == "students:top_a:v1:5"


@pytest.mark.asyncio
async def test_cache_manager_graceful_degradation_on_connection_error() -> None:
    manager = CacheManager()
    mock_client = AsyncMock()
    mock_client.get.side_effect = ConnectionError("Could not connect to Redis")
    mock_client.set.side_effect = ConnectionError("Could not connect to Redis")
    mock_client.delete.side_effect = ConnectionError("Could not connect to Redis")

    with patch.object(manager, "_get_client", return_value=mock_client):
        # Graceful degradation: khong bao gio raise exception gay 500
        get_res = await manager.get("some_key")
        assert get_res is None

        json_res = await manager.get_json("some_key")
        assert json_res is None

        set_res = await manager.set("some_key", "value")
        assert set_res is False

        set_json_res = await manager.set_json("some_key", {"k": "v"})
        assert set_json_res is False

        del_res = await manager.delete("some_key")
        assert del_res is False


@pytest.mark.asyncio
async def test_cache_manager_graceful_degradation_on_timeout() -> None:
    manager = CacheManager()
    mock_client = AsyncMock()
    mock_client.get.side_effect = TimeoutError("Redis socket timeout 500ms")

    with patch.object(manager, "_get_client", return_value=mock_client):
        result = await manager.get("timeout_key")
        assert result is None


@pytest.mark.asyncio
async def test_cache_manager_success_flow() -> None:
    manager = CacheManager()
    mock_client = AsyncMock()
    mock_client.get.return_value = '{"rank": 1, "sbd": "01000001"}'
    mock_client.set.return_value = True

    with patch.object(manager, "_get_client", return_value=mock_client):
        val = await manager.get_json("top1")
        assert val == {"rank": 1, "sbd": "01000001"}

        set_ok = await manager.set_json("top1", {"rank": 1, "sbd": "01000001"})
        assert set_ok is True
