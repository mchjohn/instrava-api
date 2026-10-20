class DomainError(Exception):
    """Base exception for domain and business rule errors."""


class EmailAlreadyRegisteredError(DomainError):
    """Raised when an email is already registered in the system."""

    def __init__(
        self,
        message: str = "E-mail já cadastrado.",
        code: str = "EMAIL_ALREADY_REGISTERED",
    ):
        self.message = message
        self.code = code
        super().__init__(self.message)
