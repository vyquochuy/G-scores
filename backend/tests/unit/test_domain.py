
from app.domain.models.exam_group import GroupA
from app.domain.models.registry import SubjectRegistry, subject_registry
from app.domain.models.subject import Subject
from app.domain.rules.scoring import (
    SCORE_BAND_LABELS,
    ScoreBand,
    classify_score_band,
)


def test_score_band_classification() -> None:
    assert classify_score_band(None) is None
    assert classify_score_band(10.0) == ScoreBand.GE_8
    assert classify_score_band(8.0) == ScoreBand.GE_8
    assert classify_score_band(7.99) == ScoreBand.GE_6_LT_8
    assert classify_score_band(6.0) == ScoreBand.GE_6_LT_8
    assert classify_score_band(5.99) == ScoreBand.GE_4_LT_6
    assert classify_score_band(4.0) == ScoreBand.GE_4_LT_6
    assert classify_score_band(3.99) == ScoreBand.LT_4
    assert classify_score_band(0.0) == ScoreBand.LT_4


def test_score_band_labels() -> None:
    assert SCORE_BAND_LABELS[ScoreBand.GE_8] == "Từ 8.0 trở lên"
    assert SCORE_BAND_LABELS[ScoreBand.GE_6_LT_8] == "Từ 6.0 đến dưới 8.0"
    assert SCORE_BAND_LABELS[ScoreBand.GE_4_LT_6] == "Từ 4.0 đến dưới 6.0"
    assert SCORE_BAND_LABELS[ScoreBand.LT_4] == "Dưới 4.0"


def test_subject_oop_properties_and_methods() -> None:
    math = Subject(code="toan", name="Toán", csv_column="toan")
    assert math.code == "toan"
    assert math.name == "Toán"
    assert math.csv_column == "toan"
    assert math.max_score == 10.0

    assert math.validate_score(8.5) is True
    assert math.validate_score(0.0) is True
    assert math.validate_score(10.0) is True
    assert math.validate_score(None) is True
    assert math.validate_score(10.5) is False
    assert math.validate_score(-0.5) is False

    assert math.classify_band(8.5) == ScoreBand.GE_8
    assert math.classify_band(None) is None


def test_group_a_calculation() -> None:
    group_a = GroupA()
    assert group_a.code == "A"
    assert "Khối A" in group_a.name
    assert group_a.required_subjects == ("toan", "vat_li", "hoa_hoc")

    # Day du 3 mon
    scores_valid = {"toan": 9.6, "vat_li": 10.0, "hoa_hoc": 10.0}
    assert group_a.calculate_total(scores_valid) == 29.60

    # Thieu mon Toan
    scores_missing_math = {"toan": None, "vat_li": 10.0, "hoa_hoc": 10.0}
    assert group_a.calculate_total(scores_missing_math) is None

    # Thieu mon Vat li
    scores_missing_phys = {"toan": 9.0, "vat_li": None, "hoa_hoc": 10.0}
    assert group_a.calculate_total(scores_missing_phys) is None

    # Thieu mon Hoa hoc
    scores_missing_chem = {"toan": 9.0, "vat_li": 8.0, "hoa_hoc": None}
    assert group_a.calculate_total(scores_missing_chem) is None


def test_subject_registry() -> None:
    registry = SubjectRegistry()
    subjects = registry.list_all()
    assert len(subjects) == 9

    codes = [s.code for s in subjects]
    expected_codes = [
        "toan",
        "ngu_van",
        "ngoai_ngu",
        "vat_li",
        "hoa_hoc",
        "sinh_hoc",
        "lich_su",
        "dia_li",
        "gdcd",
    ]
    assert codes == expected_codes

    assert registry.get("toan") is not None
    assert registry.get("TOAN") is not None
    assert registry.get("non_existent") is None

    # Singleton instance
    assert subject_registry.get("toan") is not None
    assert subject_registry.get("toan").name == "Toán"
