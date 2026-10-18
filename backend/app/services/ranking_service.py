from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.student_repo import StudentRepository
from app.schemas.student import StudentRankingItem


class RankingService:
    """Service xu ly nghiep vu xep hang thi sinh."""

    @staticmethod
    async def get_top_group_a(
        session: AsyncSession, limit: int = 10
    ) -> list[StudentRankingItem]:
        """Lay danh sach top thi sinh Khoi A (Toan, Ly, Hoa) sap xep theo tong diem giam dan.

        Khi bang diem, ap dung quy tac tie-break bang so bao danh tang dan (sbd ASC).
        """
        rows = await StudentRepository.get_top_group_a(session, limit=limit)
        items: list[StudentRankingItem] = []
        for rank, (student, total) in enumerate(rows, start=1):
            items.append(
                StudentRankingItem(
                    rank=rank,
                    registrationNumber=student.sbd,
                    math=float(student.toan or 0.0),
                    physics=float(student.vat_li or 0.0),
                    chemistry=float(student.hoa_hoc or 0.0),
                    total=total,
                )
            )
        return items
