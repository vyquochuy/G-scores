from pydantic import BaseModel, ConfigDict, Field


class StudentRankingItem(BaseModel):
    """Thong tin xep hang cua thi sinh trong Top Khoi A."""

    model_config = ConfigDict(populate_by_name=True)

    rank: int = Field(..., description="Thu hang xep theo tong diem giam dan")
    registration_number: str = Field(..., alias="registrationNumber", description="So bao danh")
    math: float = Field(..., description="Diem mon Toan")
    physics: float = Field(..., description="Diem mon Vat li")
    chemistry: float = Field(..., description="Diem mon Hoa hoc")
    total: float = Field(..., description="Tong diem 3 mon Khoi A")


class TopStudentsResponse(BaseModel):
    """Phan hoi chuan cho API Top 10 Khoi A."""

    data: list[StudentRankingItem] = Field(default_factory=list, description="Danh sach thi sinh dat thu hang cao nhat")
