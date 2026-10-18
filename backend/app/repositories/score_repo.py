from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.student import Student


class ScoreRepository:
    """Repository thuc hien cac truy van thong ke phan bo pho diem."""

    @staticmethod
    async def get_distribution_by_column(
        session: AsyncSession, column_name: str
    ) -> dict[str, int]:
        """Thuc hien thong ke 4 khoang diem va tong so thi sinh co diem cua mot mon hoc.

        Su dung cau lenh Conditional Aggregation de quet toan bo CSDL trong dung 1 cau query SQL.
        """
        col = getattr(Student, column_name, None)
        if col is None:
            raise ValueError(f"Cot '{column_name}' khong ton tai trong bang students.")

        stmt = select(
            func.count(case((col >= 8.0, 1))).label("ge_8"),
            func.count(case(((col >= 6.0) & (col < 8.0), 1))).label("ge_6_lt_8"),
            func.count(case(((col >= 4.0) & (col < 6.0), 1))).label("ge_4_lt_6"),
            func.count(case((col < 4.0, 1))).label("lt_4"),
            func.count(col).label("valid_count"),
        )
        result = await session.execute(stmt)
        row = result.one()
        return {
            "GE_8": int(row.ge_8 or 0),
            "GE_6_LT_8": int(row.ge_6_lt_8 or 0),
            "GE_4_LT_6": int(row.ge_4_lt_6 or 0),
            "LT_4": int(row.lt_4 or 0),
            "valid_count": int(row.valid_count or 0),
        }
