from sqlalchemy import Numeric, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.student import Student
from app.repositories.statistic_repo import StatisticRepository


class StudentRepository:
    """Repository thuc hien cac truy van du lieu lien quan den thi sinh."""

    @staticmethod
    async def get_by_sbd(session: AsyncSession, sbd: str) -> Student | None:
        """Tra cuu thi sinh theo so bao danh duy nhat. Su dung index idx_students_sbd."""
        stmt = select(Student).where(Student.sbd == sbd)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def total_students(session: AsyncSession) -> int:
        """Dem tong so thi sinh (uu tien doc tu system_metrics, fallback sang count(*))."""
        metric = await StatisticRepository.get_system_metric(session, "total_students")
        if metric is not None:
            return metric
        stmt = select(func.count()).select_from(Student)
        result = await session.execute(stmt)
        return int(result.scalar_one_or_none() or 0)


    @staticmethod
    async def get_top_group_a(
        session: AsyncSession, limit: int = 10
    ) -> list[tuple[Student, float]]:
        """Lay danh sach thi sinh co tong diem Khoi A cao nhat.

        Dieu kien:
        1. Thi du ca 3 mon Toan, Vat li, Hoa hoc (IS NOT NULL).
        2. Sap xep tong diem giam dan (total DESC).
        3. Tie-break: Neu bang diem, sap xep theo so bao danh tang dan (sbd ASC).
        """
        total_expr = Student.toan + Student.vat_li + Student.hoa_hoc
        stmt = (
            select(Student, cast(total_expr, Numeric(5, 2)).label("total"))
            .where(
                Student.toan.is_not(None),
                Student.vat_li.is_not(None),
                Student.hoa_hoc.is_not(None),
            )
            .order_by(total_expr.desc(), Student.sbd.asc())
            .limit(limit)
        )
        result = await session.execute(stmt)
        return [(row[0], float(row[1])) for row in result.all()]
