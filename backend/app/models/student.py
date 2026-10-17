from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sbd: Mapped[str] = mapped_column(String(8), unique=True, index=True, nullable=False)

    toan: Mapped[float | None] = mapped_column(Float, nullable=True, index=True)
    ngu_van: Mapped[float | None] = mapped_column(Float, nullable=True)
    ngoai_ngu: Mapped[float | None] = mapped_column(Float, nullable=True)
    vat_li: Mapped[float | None] = mapped_column(Float, nullable=True, index=True)
    hoa_hoc: Mapped[float | None] = mapped_column(Float, nullable=True, index=True)
    sinh_hoc: Mapped[float | None] = mapped_column(Float, nullable=True)
    lich_su: Mapped[float | None] = mapped_column(Float, nullable=True)
    dia_li: Mapped[float | None] = mapped_column(Float, nullable=True)
    gdcd: Mapped[float | None] = mapped_column(Float, nullable=True)
    ma_ngoai_ngu: Mapped[str | None] = mapped_column(String(10), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    __table_args__ = (
        Index("idx_group_a_subjects", "toan", "vat_li", "hoa_hoc"),
    )
