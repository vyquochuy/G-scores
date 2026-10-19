from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.statistic import ScoreStatistic, SystemMetric


class StatisticRepository:
    """Repository doc va ghi du lieu cac bang thong ke toi uu."""

    @staticmethod
    async def get_system_metric(session: AsyncSession, metric_key: str) -> int | None:
        """Lay gia tri cua mot chi so he thong toan cuc."""
        stmt = select(SystemMetric.metric_value).where(SystemMetric.metric_key == metric_key)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def set_system_metric(session: AsyncSession, metric_key: str, metric_value: int) -> None:
        """Luu hoac cap nhat chi so he thong toan cuc (idempotent upsert)."""
        now = datetime.now(UTC).replace(tzinfo=None)
        stmt = (
            pg_insert(SystemMetric)
            .values(
                metric_key=metric_key,
                metric_value=metric_value,
                updated_at=now,
            )
            .on_conflict_do_update(
                index_elements=[SystemMetric.metric_key],
                set_={
                    "metric_value": metric_value,
                    "updated_at": now,
                },
            )
        )
        await session.execute(stmt)

    @staticmethod
    async def get_score_statistic(
        session: AsyncSession, subject_code: str
    ) -> ScoreStatistic | None:
        """Lay ban ghi thong ke pho diem cua mot mon hoc."""
        stmt = select(ScoreStatistic).where(ScoreStatistic.subject_code == subject_code)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_score_statistics(
        session: AsyncSession,
    ) -> list[ScoreStatistic]:
        """Lay toan bo cac ban ghi thong ke pho diem da tinh toan truoc."""
        stmt = select(ScoreStatistic)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def upsert_score_statistic(
        session: AsyncSession,
        subject_code: str,
        ge_8: int,
        ge_6_lt_8: int,
        ge_4_lt_6: int,
        lt_4: int,
        valid_count: int,
    ) -> None:
        """Luu hoac cap nhat ban ghi thong ke pho diem cua mon hoc (idempotent upsert)."""
        now = datetime.now(UTC).replace(tzinfo=None)
        stmt = (
            pg_insert(ScoreStatistic)
            .values(
                subject_code=subject_code,
                ge_8=ge_8,
                ge_6_lt_8=ge_6_lt_8,
                ge_4_lt_6=ge_4_lt_6,
                lt_4=lt_4,
                valid_count=valid_count,
                updated_at=now,
            )
            .on_conflict_do_update(
                index_elements=[ScoreStatistic.subject_code],
                set_={
                    "ge_8": ge_8,
                    "ge_6_lt_8": ge_6_lt_8,
                    "ge_4_lt_6": ge_4_lt_6,
                    "lt_4": lt_4,
                    "valid_count": valid_count,
                    "updated_at": now,
                },
            )
        )
        await session.execute(stmt)
