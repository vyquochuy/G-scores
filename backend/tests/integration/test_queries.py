import pytest

from app.core.database import async_session_factory
from app.repositories.score_repo import ScoreRepository
from app.repositories.student_repo import StudentRepository


@pytest.mark.asyncio
async def test_get_by_sbd_existing_and_non_existing() -> None:
    async with async_session_factory() as session:
        student = await StudentRepository.get_by_sbd(session, "01000001")
        assert student is not None
        assert student.sbd == "01000001"
        assert student.toan == 8.4
        assert student.ngu_van == 6.75

        not_found = await StudentRepository.get_by_sbd(session, "99999999")
        assert not_found is None


@pytest.mark.asyncio
async def test_get_top_group_a() -> None:
    async with async_session_factory() as session:
        top_list = await StudentRepository.get_top_group_a(session, limit=10)
        assert len(top_list) == 10

        # Thu khoa Khoi A
        first_student, first_total = top_list[0]
        assert first_student.sbd == "26020938"
        assert first_total == 29.60
        assert first_student.toan == 9.6
        assert first_student.vat_li == 10.0
        assert first_student.hoa_hoc == 10.0

        # Kiem tra thu tu giam dan cua tong diem
        for i in range(len(top_list) - 1):
            assert top_list[i][1] >= top_list[i + 1][1]


@pytest.mark.asyncio
async def test_get_score_distribution_toan() -> None:
    async with async_session_factory() as session:
        dist = await ScoreRepository.get_distribution_by_column(session, "toan")
        assert dist["valid_count"] == 1045613
        assert dist["GE_8"] == 198392
        assert dist["GE_6_LT_8"] == 505836
        assert dist["GE_4_LT_6"] == 258654
        assert dist["LT_4"] == 82731
        # Tong 4 khoang bang chinh xac valid_count
        assert (
            dist["GE_8"] + dist["GE_6_LT_8"] + dist["GE_4_LT_6"] + dist["LT_4"]
            == dist["valid_count"]
        )
