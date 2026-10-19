import logging

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import CACHE_TTL_24H, cache_manager, get_distribution_cache_key
from app.core.exceptions import AppValidationException
from app.domain.models.registry import subject_registry
from app.domain.rules.scoring import SCORE_BAND_LABELS, ScoreBand
from app.repositories.score_repo import ScoreRepository
from app.repositories.statistic_repo import StatisticRepository
from app.schemas.report import (
    ScoreBandItem,
    ScoreDistributionData,
    SubjectItem,
)

logger = logging.getLogger(__name__)


class ReportService:
    """Service xu ly nghiep vu thong ke pho diem va danh muc mon hoc."""

    @staticmethod
    async def get_score_distribution(
        session: AsyncSession, subject_code: str
    ) -> ScoreDistributionData:
        clean_code = subject_code.strip().lower() if subject_code else ""
        cache_key = get_distribution_cache_key(clean_code)
        cached_data = await cache_manager.get_json(cache_key)
        if cached_data is not None:
            try:
                return ScoreDistributionData.model_validate(cached_data)
            except (ValidationError, TypeError, KeyError) as exc:
                logger.warning("Loi giai ma cache pho diem: %s. Chuyen truy van PostgreSQL.", exc)


        if clean_code in ("all", "tat_ca"):
            total_counts = {
                ScoreBand.GE_8.value: 0,
                ScoreBand.GE_6_LT_8.value: 0,
                ScoreBand.GE_4_LT_6.value: 0,
                ScoreBand.LT_4.value: 0,
                "valid_count": 0,
            }
            stats = await StatisticRepository.get_all_score_statistics(session)
            if len(stats) >= len(subject_registry.list_all()):
                for st in stats:
                    total_counts[ScoreBand.GE_8.value] += st.ge_8
                    total_counts[ScoreBand.GE_6_LT_8.value] += st.ge_6_lt_8
                    total_counts[ScoreBand.GE_4_LT_6.value] += st.ge_4_lt_6
                    total_counts[ScoreBand.LT_4.value] += st.lt_4
                    total_counts["valid_count"] += st.valid_count
            else:
                for sub in subject_registry.list_all():
                    sub_counts = await ScoreRepository.get_distribution(
                        session, sub.code, sub.csv_column
                    )
                    for k in total_counts:
                        total_counts[k] += sub_counts[k]

            bands = [
                ScoreBandItem(
                    key=ScoreBand.GE_8.value,
                    label=SCORE_BAND_LABELS[ScoreBand.GE_8],
                    count=total_counts[ScoreBand.GE_8.value],
                ),
                ScoreBandItem(
                    key=ScoreBand.GE_6_LT_8.value,
                    label=SCORE_BAND_LABELS[ScoreBand.GE_6_LT_8],
                    count=total_counts[ScoreBand.GE_6_LT_8.value],
                ),
                ScoreBandItem(
                    key=ScoreBand.GE_4_LT_6.value,
                    label=SCORE_BAND_LABELS[ScoreBand.GE_4_LT_6],
                    count=total_counts[ScoreBand.GE_4_LT_6.value],
                ),
                ScoreBandItem(
                    key=ScoreBand.LT_4.value,
                    label=SCORE_BAND_LABELS[ScoreBand.LT_4],
                    count=total_counts[ScoreBand.LT_4.value],
                ),
            ]

            result = ScoreDistributionData(
                subjectCode="all",
                subjectName="Tất cả môn học",
                validScoreCount=total_counts["valid_count"],
                bands=bands,
            )
            await cache_manager.set_json(
                cache_key,
                result.model_dump(by_alias=True),
                ttl_seconds=CACHE_TTL_24H,
            )
            return result

        subject = subject_registry.get(clean_code)
        if not subject:
            raise AppValidationException(
                f"Mã môn học '{subject_code}' không hợp lệ hoặc không tồn tại trong hệ thống."
            )

        counts = await ScoreRepository.get_distribution(
            session, subject.code, subject.csv_column
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

        result = ScoreDistributionData(
            subjectCode=subject.code,
            subjectName=subject.name,
            validScoreCount=counts["valid_count"],
            bands=bands,
        )
        await cache_manager.set_json(
            cache_key,
            result.model_dump(by_alias=True),
            ttl_seconds=CACHE_TTL_24H,
        )
        return result

    @staticmethod

    def get_all_subjects() -> list[SubjectItem]:
        """Lay danh muc toan bo cac mon hoc duoc ho tro trong he thong."""
        return [
            SubjectItem(code=sub.code, name=sub.name)
            for sub in subject_registry.list_all()
        ]
