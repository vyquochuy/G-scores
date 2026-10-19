"""Module quan ly Redis Cache bat dong bo theo mo hinh Cache-Aside.

Dac tinh ky thuat:
1. Timeout ket noi ngan (500ms) chong nghen tien trinh API khi gap su co mang.
2. Graceful Degradation (Suy giam tinh nang co kiem soat): Neu Redis timeout,
   loi ket noi hoac chua khoi dong, module bat ngoai le an toan va tra ve None/False
   de tang Service tu dong fallback sang truy van PostgreSQL.
3. Chinh sach TTL 24 gio (86,400 giay) kem key versioning (v1).
"""

import json
import logging
from typing import Any

try:
    from redis.asyncio import ConnectionPool, Redis
    from redis.exceptions import RedisError
    REDIS_AVAILABLE = True
except ImportError:
    ConnectionPool = None  # type: ignore[assignment,misc]
    Redis = None  # type: ignore[assignment,misc]
    RedisError = Exception  # type: ignore[assignment,misc]
    REDIS_AVAILABLE = False

from app.core.config import settings

logger = logging.getLogger(__name__)

# Hang so dinh danh khoa cache (Key versioning) va TTL
CACHE_TTL_24H = 86400  # 24 gio
KEY_STUDENTS_TOTAL = "students:total:v1"
KEY_TOP_A_PREFIX = "students:top_a:v1"
KEY_REPORTS_DISTRIBUTION_PREFIX = "reports:distribution:v1"


def get_distribution_cache_key(subject_code: str) -> str:
    """Sinh khoa cache cho bao cao pho diem theo mon hoc."""
    clean = subject_code.strip().lower() if subject_code else "all"
    return f"{KEY_REPORTS_DISTRIBUTION_PREFIX}:{clean}"


def get_top_a_cache_key(limit: int = 10) -> str:
    """Sinh khoa cache cho danh sach top thi sinh Khoi A."""
    return f"{KEY_TOP_A_PREFIX}:{limit}"


class CacheManager:
    """Quan ly ket noi va thao tac doc/ghi Redis Cache bat dong bo."""

    def __init__(self) -> None:
        self._pool: ConnectionPool | None = None
        self._client: Redis | None = None

    def _get_client(self) -> Redis | None:
        """Khoi tao ket noi Redis client voi co che lazy initialization va timeout chat che."""
        if not settings.REDIS_URL or not REDIS_AVAILABLE:
            return None

        if self._client is None:
            try:
                self._pool = ConnectionPool.from_url(
                    settings.REDIS_URL,
                    socket_connect_timeout=settings.REDIS_TIMEOUT_SECONDS,
                    socket_timeout=settings.REDIS_TIMEOUT_SECONDS,
                    max_connections=20,
                    decode_responses=True,
                )
                self._client = Redis(connection_pool=self._pool)
            except (RedisError, TimeoutError, OSError, ValueError) as exc:
                logger.warning("Khong the khoi tao Redis Connection Pool: %s. Chuyen che do fallback.", exc)
                return None


        return self._client

    async def get(self, key: str) -> str | None:
        """Doc chuoi ky tu tu Redis. Tra ve None neu cache miss hoac Redis gap su co."""
        client = self._get_client()
        if client is None:
            return None

        try:
            return await client.get(key)
        except (RedisError, TimeoutError, OSError) as exc:
            logger.warning("Redis GET loi tren khoa '%s': %s. Tu dong fallback sang CSDL.", key, exc)
            return None

    async def get_json(self, key: str) -> Any | None:
        """Doc va giai ma chuoi JSON tu Redis. Tra ve None neu cache miss hoac loi."""
        raw_val = await self.get(key)
        if raw_val is None:
            return None
        try:
            return json.loads(raw_val)
        except (json.JSONDecodeError, TypeError) as exc:
            logger.warning("Loi giai ma JSON tu cache cho khoa '%s': %s", key, exc)
            return None

    async def set(self, key: str, value: str, ttl_seconds: int = CACHE_TTL_24H) -> bool:
        """Luu chuoi vao Redis voi thoi gian song TTL. Tra ve False neu that bai."""
        client = self._get_client()
        if client is None:
            return False

        try:
            await client.set(key, value, ex=ttl_seconds)
            return True
        except (RedisError, TimeoutError, OSError) as exc:
            logger.warning("Redis SET loi tren khoa '%s': %s. Bo qua ghi cache.", key, exc)
            return False

    async def set_json(self, key: str, value: Any, ttl_seconds: int = CACHE_TTL_24H) -> bool:
        """Ma hoa JSON va luu vao Redis voi TTL."""
        try:
            encoded = json.dumps(value, ensure_ascii=False)
            return await self.set(key, encoded, ttl_seconds=ttl_seconds)
        except (TypeError, ValueError) as exc:
            logger.warning("Loi ma hoa JSON khi ghi cache cho khoa '%s': %s", key, exc)
            return False

    async def delete(self, key: str) -> bool:
        """Xoa khoa khoi Redis."""
        client = self._get_client()
        if client is None:
            return False
        try:
            await client.delete(key)
            return True
        except (RedisError, TimeoutError, OSError) as exc:
            logger.warning("Redis DELETE loi tren khoa '%s': %s", key, exc)
            return False

    async def close(self) -> None:
        """Dong ket noi va giai phong connection pool."""
        if self._client is not None:
            try:
                await self._client.aclose()
            except (RedisError, OSError) as exc:
                logger.debug("Loi khi dong Redis client: %s", exc)
            self._client = None
        if self._pool is not None:
            try:
                await self._pool.aclose()
            except (RedisError, OSError) as exc:
                logger.debug("Loi khi dong Redis pool: %s", exc)
            self._pool = None



# Singleton instance CacheManager su dung xuyen suot backend
cache_manager = CacheManager()
