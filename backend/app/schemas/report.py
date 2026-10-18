from pydantic import BaseModel, ConfigDict, Field


class ScoreBandItem(BaseModel):
    """So luong thi sinh trong mot khoang diem."""

    key: str = Field(..., description="Ma khoang pho diem (GE_8, GE_6_LT_8, GE_4_LT_6, LT_4)")
    label: str = Field(..., description="Nhan hien thi tieng Viet co dau")
    count: int = Field(..., description="So luong thi sinh nam trong khoang")


class ScoreDistributionData(BaseModel):
    """Du lieu bao cao pho diem cua mot mon hoc."""

    model_config = ConfigDict(populate_by_name=True)

    subject_code: str = Field(..., alias="subjectCode", description="Ma mon hoc")
    subject_name: str = Field(..., alias="subjectName", description="Ten mon hoc tieng Viet co dau")
    valid_score_count: int = Field(..., alias="validScoreCount", description="Tong so thi sinh co diem thi hop le")
    bands: list[ScoreBandItem] = Field(default_factory=list, description="Thong ke theo 4 khoang diem")


class ScoreDistributionResponse(BaseModel):
    """Phan hoi chuan cho API thong ke pho diem."""

    data: ScoreDistributionData


class SubjectItem(BaseModel):
    """Thong tin mot mon hoc trong danh muc he thong."""

    code: str = Field(..., description="Ma dinh danh mon hoc")
    name: str = Field(..., description="Ten day du cua mon hoc tieng Viet co dau")


class SubjectsResponse(BaseModel):
    """Phan hoi chuan cho API danh muc mon hoc."""

    data: list[SubjectItem] = Field(default_factory=list, description="Danh sach cac mon hoc duoc ho tro")
