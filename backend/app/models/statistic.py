from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SystemMetric(Base):
    """Luu tru cac chi so he thong toan cuc tinh nhu tong so thi sinh."""

    __tablename__ = "system_metrics"

    metric_key: Mapped[str] = mapped_column(String(50), primary_key=True)
    metric_value: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
        onupdate=lambda: datetime.now(UTC).replace(tzinfo=None),
        nullable=False,
    )


class ScoreStatistic(Base):
    """Luu tru thong ke phan bo 4 khoang pho diem va so luong diem hop le cua cac mon hoc."""

    __tablename__ = "score_statistics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subject_code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    ge_8: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ge_6_lt_8: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ge_4_lt_6: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    lt_4: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    valid_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
        onupdate=lambda: datetime.now(UTC).replace(tzinfo=None),
        nullable=False,
    )
