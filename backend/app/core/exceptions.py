class AppException(Exception):
    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class AppEntityNotFoundException(AppException):
    def __init__(self, message: str = "Khong tim thay ban ghi theo yeu cau."):
        super().__init__(message=message, code="NOT_FOUND")


class AppValidationException(AppException):
    def __init__(self, message: str = "Du lieu dau vao khong hop le."):
        super().__init__(message=message, code="VALIDATION_ERROR")
