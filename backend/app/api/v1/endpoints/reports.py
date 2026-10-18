from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.schemas.report import ScoreDistributionResponse
from app.services.report_service import ReportService

router = APIRouter()


@router.get(
    "/score-distribution",
    response_model=ScoreDistributionResponse,
    summary="Thống kê phổ điểm theo môn học",
    description="Thống kê số lượng thí sinh theo 4 khoảng điểm (>=8, 6-8, 4-6, <4) của một môn học.",
)
async def get_score_distribution(
    subject_code: str = Query(
        ...,
        alias="subjectCode",
        description="Mã môn học cần thống kê (ví dụ: toan, vat_li, hoa_hoc)",
        examples=["toan"],
    ),
    session: AsyncSession = Depends(get_db_session),
) -> ScoreDistributionResponse:
    data = await ReportService.get_score_distribution(session, subject_code)
    return ScoreDistributionResponse(data=data)
