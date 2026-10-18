import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RegistrationNumberParam(BaseModel):
    """Tham so so bao danh thi sinh can tra cuu."""

    sbd: str = Field(..., description="So bao danh thi sinh gom dung 8 chu so")

    @field_validator("sbd")
    @classmethod
    def validate_sbd_format(cls, v: str) -> str:
        clean_v = v.strip()
        if not re.match(r"^\d{8}$", clean_v):
            raise ValueError("Số báo danh phải bao gồm đúng 8 chữ số.")
        return clean_v


class SubjectScoreItem(BaseModel):
    """Diem cua mot mon thi."""

    model_config = ConfigDict(populate_by_name=True)

    subject_code: str = Field(..., alias="subjectCode", description="Ma mon hoc")
    subject_name: str = Field(..., alias="subjectName", description="Ten mon hoc tieng Viet co dau")
    score: float = Field(..., description="Diem so thuc te")


class StudentScoresData(BaseModel):
    """Du lieu tra cuu diem thi cua mot thi sinh."""

    model_config = ConfigDict(populate_by_name=True)

    registration_number: str = Field(..., alias="registrationNumber", description="So bao danh thi sinh")
    scores: list[SubjectScoreItem] = Field(default_factory=list, description="Danh sach cac mon thi va diem so")


class StudentScoresResponse(BaseModel):
    """Phan hoi chuan cho API tra cuu diem."""

    data: StudentScoresData
