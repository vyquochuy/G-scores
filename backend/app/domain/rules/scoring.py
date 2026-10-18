from enum import Enum


class ScoreBand(str, Enum):
    """Cac khoang pho diem theo quy dinh cua de bai."""

    GE_8 = "GE_8"  # >= 8.0
    GE_6_LT_8 = "GE_6_LT_8"  # 6.0 <= score < 8.0
    GE_4_LT_6 = "GE_4_LT_6"  # 4.0 <= score < 6.0
    LT_4 = "LT_4"  # < 4.0


SCORE_BAND_LABELS: dict[ScoreBand, str] = {
    ScoreBand.GE_8: "Từ 8.0 trở lên",
    ScoreBand.GE_6_LT_8: "Từ 6.0 đến dưới 8.0",
    ScoreBand.GE_4_LT_6: "Từ 4.0 đến dưới 6.0",
    ScoreBand.LT_4: "Dưới 4.0",
}


def classify_score_band(score: float | None) -> ScoreBand | None:
    """Phan loai diem so vao 4 khoang tieu chuan.

    Tra ve None neu diem la None (thi sinh khong thi hoac khong co diem).
    """
    if score is None:
        return None
    if score >= 8.0:
        return ScoreBand.GE_8
    if score >= 6.0:
        return ScoreBand.GE_6_LT_8
    if score >= 4.0:
        return ScoreBand.GE_4_LT_6
    return ScoreBand.LT_4
