from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppValidationException
from app.domain.models.registry import subject_registry
from app.domain.rules.scoring import SCORE_BAND_LABELS, ScoreBand
from app.repositories.score_repo import ScoreRepository
from app.schemas.report import (
    ScoreBandItem,
    ScoreDistributionData,
    SubjectItem,
)


class ReportService:
    """Service xu ly nghiep vu thong ke pho diem va danh muc mon hoc."""

    @staticmethod
    async def get_score_distribution(
        session: AsyncSession, subject_code: str
    ) -> ScoreDistributionData:
        clean_code = subject_code.strip().lower() if subject_code else ""
        subject = subject_registry.get(clean_code)
        if not subject:
            raise AppValidationException(
                f"Mã môn học '{subject_code}' không hợp lệ hoặc không tồn tại trong hệ thống."
            )

        counts = await ScoreRepository.get_distribution_by_column(
            session, subject.csv_column
        )

        bands = [
            ScoreBandItem(
                key=ScoreBand.GE_8.value,
                label=SCORE_BAND_LABELS[ScoreBand.GE_8],
                count=counts[ScoreBand.GE_8.value],
            ),
            ScoreBandItem(
                key=ScoreBand.GE_6_LT_8.value,
                label=SCORE_BAND_LABELS[ScoreBand.GE_6_LT_8],
                count=counts[ScoreBand.GE_6_LT_8.value],
            ),
            ScoreBandItem(
                key=ScoreBand.GE_4_LT_6.value,
                label=SCORE_BAND_LABELS[ScoreBand.GE_4_LT_6],
                count=counts[ScoreBand.GE_4_LT_6.value],
            ),
            ScoreBandItem(
                key=ScoreBand.LT_4.value,
                label=SCORE_BAND_LABELS[ScoreBand.LT_4],
                count=counts[ScoreBand.LT_4.value],
            ),
        ]

        return ScoreDistributionData(
            subjectCode=subject.code,
            subjectName=subject.name,
            validScoreCount=counts["valid_count"],
            bands=bands,
        )

    @staticmethod
    def get_all_subjects() -> list[SubjectItem]:
        """Lay danh muc toan bo cac mon hoc duoc ho tro trong he thong."""
        return [
            SubjectItem(code=sub.code, name=sub.name)
            for sub in subject_registry.list_all()
        ]
