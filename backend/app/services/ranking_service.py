import logging

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import CACHE_TTL_24H, cache_manager, get_top_a_cache_key
from app.repositories.student_repo import StudentRepository
from app.schemas.student import StudentRankingItem

logger = logging.getLogger(__name__)



class RankingService:
    """Service xu ly nghiep vu xep hang thi sinh."""

    @staticmethod
    async def get_top_group_a(
        session: AsyncSession, limit: int = 10
    ) -> list[StudentRankingItem]:
        """Lay danh sach top thi sinh Khoi A (Toan, Ly, Hoa) sap xep theo tong diem giam dan.

        Khi bang diem, ap dung quy tac tie-break bang so bao danh tang dan (sbd ASC).
        Ap dung mo hinh Cache-Aside voi Redis cache (TTL 24h) va fallback tu dong sang PostgreSQL.
        """
        cache_key = get_top_a_cache_key(limit)
        cached_data = await cache_manager.get_json(cache_key)
        if cached_data is not None:
            try:
                return [StudentRankingItem.model_validate(item) for item in cached_data]
            except (ValidationError, TypeError, KeyError) as exc:
                logger.warning("Loi giai ma cache Top A: %s. Chuyen truy van PostgreSQL.", exc)


        rows = await StudentRepository.get_top_group_a(session, limit=limit)
        items: list[StudentRankingItem] = []
        for rank, (student, total) in enumerate(rows, start=1):
            items.append(
                StudentRankingItem(
                    rank=rank,
                    registrationNumber=student.sbd,
                    math=float(student.toan or 0.0),
                    physics=float(student.vat_li or 0.0),
                    chemistry=float(student.hoa_hoc or 0.0),
                    total=total,
                )
            )

        # Ghi vao cache khong dong bo (fire-and-forget an toan)
        await cache_manager.set_json(
            cache_key,
            [item.model_dump(by_alias=True) for item in items],
            ttl_seconds=CACHE_TTL_24H,
        )
        return items

