from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
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
