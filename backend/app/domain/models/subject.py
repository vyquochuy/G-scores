from app.domain.rules.scoring import ScoreBand, classify_score_band


class Subject:
    """Lop thuc the dai dien cho mot mon hoc theo quy tac lap trinh huong doi tuong (OOP)."""

    def __init__(
        self,
        code: str,
        name: str,
        csv_column: str,
        max_score: float = 10.0,
    ) -> None:
        self._code = code.strip().lower()
        self._name = name.strip()
        self._csv_column = csv_column.strip().lower()
        self._max_score = max_score

    @property
    def code(self) -> str:
        return self._code

    @property
    def name(self) -> str:
        return self._name

    @property
    def csv_column(self) -> str:
        return self._csv_column

    @property
    def max_score(self) -> float:
        return self._max_score

    def validate_score(self, score: float | None) -> bool:
        """Kiem tra xem diem co hop le trong thang diem 0 - max_score hay khong."""
        if score is None:
            return True
        return 0.0 <= score <= self._max_score

    def classify_band(self, score: float | None) -> ScoreBand | None:
        """Phan loai diem so cua mon hoc vao khoang pho diem tieu chuan."""
        return classify_score_band(score)

    def __repr__(self) -> str:
        return f"Subject(code='{self._code}', name='{self._name}')"
