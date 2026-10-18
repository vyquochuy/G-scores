import re

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppEntityNotFoundException, AppValidationException
from app.domain.models.registry import subject_registry
from app.repositories.student_repo import StudentRepository
from app.schemas.score import StudentScoresData, SubjectScoreItem


class LookupService:
    """Service xu ly nghiep vu tra cuu diem thi theo so bao danh."""

    @staticmethod
    async def lookup_by_sbd(session: AsyncSession, sbd: str) -> StudentScoresData:
        clean_sbd = sbd.strip() if sbd else ""
        if not re.match(r"^\d{8}$", clean_sbd):
            raise AppValidationException("Số báo danh phải bao gồm đúng 8 chữ số.")

        student = await StudentRepository.get_by_sbd(session, clean_sbd)
        if not student:
            raise AppEntityNotFoundException("Không tìm thấy thí sinh với số báo danh đã cung cấp.")

        scores: list[SubjectScoreItem] = []
        for subject in subject_registry.list_all():
            val = getattr(student, subject.csv_column, None)
            if val is not None:
                scores.append(
                    SubjectScoreItem(
                        subjectCode=subject.code,
                        subjectName=subject.name,
                        score=float(val),
                    )
                )

        return StudentScoresData(
            registrationNumber=student.sbd,
            scores=scores,
        )
