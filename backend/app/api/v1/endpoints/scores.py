from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.schemas.score import StudentScoresResponse
from app.services.lookup_service import LookupService

router = APIRouter()


@router.get(
    "/{registration_number}",
    response_model=StudentScoresResponse,
    summary="Tra cứu điểm thi theo số báo danh",
    description="Tra cứu điểm thi THPT 2024 của một thí sinh dựa trên số báo danh (8 chữ số).",
)
async def get_student_scores(
    registration_number: str = Path(
        ...,
        description="Số báo danh thí sinh gồm đúng 8 chữ số (ví dụ: 01000001)",
        examples=["01000001"],
    ),
    session: AsyncSession = Depends(get_db_session),
) -> StudentScoresResponse:


    data = await LookupService.lookup_by_sbd(session, registration_number)
    return StudentScoresResponse(data=data)
