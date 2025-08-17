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


class EntityNotFoundError(AppExceptionError):
    """Exception raised when an entity is not found."""

    default_message = "Entity not found."
    status_code = 404


class EntityAlreadyExistsError(AppExceptionError):
    """Exception raised when an entity already exists."""

    default_message = "Entity already exists."
    status_code = 409


class AuthError(AppExceptionError):
    """Exception raised for authentication errors."""

    default_message = "Authentication error occurred."
    status_code = 401
