from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import CACHE_TTL_24H, KEY_STUDENTS_TOTAL, cache_manager
from app.core.database import get_db_session
from app.repositories.student_repo import StudentRepository
from app.schemas.student import TopStudentsResponse
from app.services.ranking_service import RankingService

router = APIRouter()


@router.get(
    "/top-a",
    response_model=TopStudentsResponse,
    summary="Bảng xếp hạng Top 10 thí sinh Khối A",
    description="Lấy danh sách 10 thí sinh có tổng điểm 3 môn Khối A (Toán, Vật lí, Hóa học) cao nhất.",
)
async def get_top_students_group_a(
    session: AsyncSession = Depends(get_db_session),
) -> TopStudentsResponse:
    data = await RankingService.get_top_group_a(session, limit=10)
    return TopStudentsResponse(data=data)


@router.get(
    "/total",
    summary="Lấy tổng số thí sinh dự thi",
)
async def get_total_students(
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    cached_val = await cache_manager.get(KEY_STUDENTS_TOTAL)
    if cached_val is not None:
        try:
            return {"data": {"total": int(cached_val)}}
        except ValueError:
            pass

    total = await StudentRepository.total_students(session)
    await cache_manager.set(KEY_STUDENTS_TOTAL, str(total), ttl_seconds=CACHE_TTL_24H)
    return {"data": {"total": total}}