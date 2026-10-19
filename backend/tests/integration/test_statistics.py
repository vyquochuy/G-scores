import pytest

from app.core.database import async_session_factory
from app.repositories.score_repo import ScoreRepository
from app.repositories.statistic_repo import StatisticRepository
from app.repositories.student_repo import StudentRepository


@pytest.mark.asyncio
async def test_statistic_repository_and_ground_truth() -> None:
    async with async_session_factory() as session:
        # Kiem tra total_students
        total = await StudentRepository.total_students(session)
        assert total == 1061605

        system_metric_total = await StatisticRepository.get_system_metric(session, "total_students")
        assert system_metric_total == 1061605

        # Kiem tra score_statistics cho mon toan
        stat_toan = await StatisticRepository.get_score_statistic(session, "toan")
        assert stat_toan is not None
        assert stat_toan.valid_count == 1045613
        assert stat_toan.ge_8 == 198392
        assert stat_toan.ge_6_lt_8 == 505836
        assert stat_toan.ge_4_lt_6 == 258654
        assert stat_toan.lt_4 == 82731

        # Kiem tra get_distribution voi fallback
        dist = await ScoreRepository.get_distribution(session, "toan", "toan")
        assert dist["valid_count"] == 1045613
        assert dist["GE_8"] == 198392
        assert dist["GE_6_LT_8"] == 505836
        assert dist["GE_4_LT_6"] == 258654
        assert dist["LT_4"] == 82731
