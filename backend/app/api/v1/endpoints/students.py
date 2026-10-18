from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.schemas.student import TopStudentsResponse
from app.services.ranking_service import RankingService
from app.repositories.student_repo import StudentRepository

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
    total = await StudentRepository.total_students(session)
    return {"data": {"total": total}}