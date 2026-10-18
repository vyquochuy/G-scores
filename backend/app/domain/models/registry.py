from app.domain.models.subject import Subject


class SubjectRegistry:
    """Registry quan ly tap trung danh muc cac mon hoc cua he thong."""

    def __init__(self) -> None:
        self._subjects: dict[str, Subject] = {}
        self._register_defaults()

    def register(self, subject: Subject) -> None:
        """Dang ky mot mon hoc moi vao registry."""
        self._subjects[subject.code] = subject

    def get(self, code: str) -> Subject | None:
        """Lay mon hoc theo ma code (khong phan biet hoa thuong)."""
        if not code:
            return None
        return self._subjects.get(code.strip().lower())

    def list_all(self) -> list[Subject]:
        """Tra ve danh sach tat ca cac mon hoc da dang ky theo thu tu chuan."""
        return list(self._subjects.values())

    def _register_defaults(self) -> None:
        defaults = [
            Subject(code="toan", name="Toán", csv_column="toan"),
            Subject(code="ngu_van", name="Ngữ văn", csv_column="ngu_van"),
            Subject(code="ngoai_ngu", name="Ngoại ngữ", csv_column="ngoai_ngu"),
            Subject(code="vat_li", name="Vật lí", csv_column="vat_li"),
            Subject(code="hoa_hoc", name="Hóa học", csv_column="hoa_hoc"),
            Subject(code="sinh_hoc", name="Sinh học", csv_column="sinh_hoc"),
            Subject(code="lich_su", name="Lịch sử", csv_column="lich_su"),
            Subject(code="dia_li", name="Địa lí", csv_column="dia_li"),
            Subject(code="gdcd", name="Giáo dục công dân", csv_column="gdcd"),
        ]
        for subject in defaults:
            self.register(subject)


# Singleton instance su dung xuyen suot toan bo backend
subject_registry = SubjectRegistry()
