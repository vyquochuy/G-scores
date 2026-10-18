from abc import ABC, abstractmethod


class ExamGroup(ABC):
    """Lop truu tuong dai dien cho to hop xet tuyen dai hoc."""

    @property
    @abstractmethod
    def code(self) -> str:
        """Ma to hop xet tuyen (vi du: 'A', 'B', 'C')."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Ten day du cua to hop xet tuyen."""

    @property
    @abstractmethod
    def required_subjects(self) -> tuple[str, ...]:
        """Danh sach ma cac mon hoc bat buoc phai co trong to hop."""

    @abstractmethod
    def calculate_total(self, scores: dict[str, float | None]) -> float | None:
        """Tinh tong diem xet tuyen neu thi sinh thi du tat ca cac mon bat buoc.

        Tra ve None neu thi sinh vang thi bat ky mon nao.
        """


class GroupA(ExamGroup):
    """Khoi A gom 3 mon bat buoc: Toan, Vat li, Hoa hoc."""

    REQUIRED_SUBJECTS = ("toan", "vat_li", "hoa_hoc")

    @property
    def code(self) -> str:
        return "A"

    @property
    def name(self) -> str:
        return "Khối A (Toán, Vật lí, Hóa học)"

    @property
    def required_subjects(self) -> tuple[str, ...]:
        return self.REQUIRED_SUBJECTS

    def calculate_total(self, scores: dict[str, float | None]) -> float | None:
        math = scores.get("toan")
        physics = scores.get("vat_li")
        chemistry = scores.get("hoa_hoc")

        # Bat buoc phai co du ca 3 mon thi, thieu bat ky mon nao deu bi loai
        if math is None or physics is None or chemistry is None:
            return None

        return round(math + physics + chemistry, 2)
