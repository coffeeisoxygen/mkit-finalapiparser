# src/exception/exceptions.py

from app.config import get_settings

APP_NAME = get_settings().app_name


# =========================
# Base & Specific Exceptions
# =========================
class AppExceptionError(Exception):
    """Base exception with adapter support."""

    default_message: str = "An application error occurred."
    status_code: int = 500

    def __init__(
        self,
        message: str | None = None,
        name: str = APP_NAME,
        context: dict | None = None,
        cause: Exception | None = None,
    ):
        self.message = message or self.default_message
        self.name = name
        self.context = context or {}
        self.__cause__ = cause
        super().__init__(self.message)


# Member Auth Error should Group In Entitiy Error


class EntityExcError(AppExceptionError):
    default_message = "Entity error occurred."
    status_code = 400
