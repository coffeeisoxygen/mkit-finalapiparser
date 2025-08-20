# src/exception/exceptions.py

from typing import Any

from app.config import get_settings

APP_NAME = get_settings().APP_NAME


# ----------------- Base Exception -----------------
class AppExceptionError(Exception):
    """Base exception with adapter support and proper chaining."""

    default_message: str = "An application error occurred."
    status_code: int | None = None  # subclass wajib override

    def __init__(
        self,
        message: str | None = None,
        name: str = APP_NAME,
        context: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ):
        self.message = message or self.default_message
        self.name = name
        self.context = context or {}
        self.__cause__ = cause  # built-in chaining

        super().__init__(self._compose_message())

    def _compose_message(self) -> str:
        """Bikin message final dengan cause kalau ada."""
        if self.__cause__:
            return f"{self.message} (caused by {type(self.__cause__).__name__}: {self.__cause__})"
        return self.message

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "message": self.message,
            "status_code": self.status_code,
            "context": self.context,
            "cause": str(self.__cause__) if self.__cause__ else None,
        }

    def __str__(self) -> str:
        return self._compose_message()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} status={self.status_code} message={self.message!r}>"


# ----------------- Data Integrity Exceptions -----------------
class DataIntegrityError(AppExceptionError):
    """Exception raised for data integrity errors."""

    default_message = "Data integrity error occurred."
    status_code = 409


class DataNotFoundError(DataIntegrityError):
    """Exception raised when data is not found."""

    default_message = "Data not found."
    status_code = 404


class DataDuplicationError(DataIntegrityError):
    """Exception raised for data duplication errors."""

    default_message = "Data duplication error occurred."
    status_code = 409


class DataGenericError(DataIntegrityError):
    """Exception raised for generic data errors."""

    default_message = "Generic data error occurred."
    status_code = 400


class InternalSeedingError(AppExceptionError):
    """Exception raised for internal seeding errors."""

    default_message = "Internal seeding error occurred."
    status_code = 500


# ----------------- Entity Exceptions -----------------
class EntityNotFoundError(AppExceptionError):
    """Exception raised when an entity is not found."""

    default_message = "Entity not found."
    status_code = 404


class EntityAlreadyExistsError(AppExceptionError):
    """Exception raised when an entity already exists."""

    default_message = "Entity already exists."
    status_code = 409


# ----------------- Audit Exceptions -----------------
class AuditMixinError(AppExceptionError):
    """Exception raised for audit mixin errors."""

    default_message = "Audit mixin error occurred."
    status_code = 500


class AdminCantDeleteError(AppExceptionError):
    """Exception raised when an admin user cannot be deleted."""

    default_message = "Admin user cannot be deleted."
    status_code = 403


# ----------------- Auth Exceptions -----------------
class AuthError(AppExceptionError):
    """Exception raised for authentication errors."""

    default_message = "Authentication error occurred."
    status_code = 401


class TokenExpiredError(AuthError):
    """Exception raised when a token has expired."""

    default_message = "Token has expired."
    status_code = 401


class TokenInvalidError(AuthError):
    """Exception raised when a token is invalid."""

    default_message = "Token is invalid."
    status_code = 401


class UserNotFoundError(AuthError):
    """Exception raised when a user is not found."""

    default_message = "User not found."
    status_code = 404


class UserPasswordError(AuthError):
    """Exception raised when a user's password is incorrect."""

    default_message = "Incorrect password."
    status_code = 401


# ----------------- Service Exceptions -----------------
class ServiceError(AppExceptionError):
    """Exception raised for service errors."""

    default_message = "Service error occurred."
    status_code = 503
