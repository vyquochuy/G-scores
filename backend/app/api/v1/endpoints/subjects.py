from fastapi import APIRouter

from app.schemas.report import SubjectsResponse
from app.services.report_service import ReportService

router = APIRouter()


@router.get(
    "",
    response_model=SubjectsResponse,
    summary="Danh mục môn học",
    description="Lấy danh mục toàn bộ các môn học thi tốt nghiệp THPT được hệ thống hỗ trợ.",
)
async def list_subjects() -> SubjectsResponse:
    subjects = ReportService.get_all_subjects()
    return SubjectsResponse(data=subjects)
