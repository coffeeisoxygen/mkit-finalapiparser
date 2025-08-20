import uuid
from abc import ABC, abstractmethod
from typing import Any, TypeVar

T = TypeVar("T")


class IUserRepo[T](ABC):
    @abstractmethod
    async def create(self, data: dict[str, Any]) -> T:
        """Create a new user from a dict of fields."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, id: uuid.UUID) -> T | None:
        """Get user by unique id."""
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list[T]:
        """Get all users."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, id: uuid.UUID, updates: dict[str, Any]) -> T:
        """Update user fields by id with provided updates (granular)."""
        raise NotImplementedError

    @abstractmethod
    async def soft_delete(self, id: uuid.UUID) -> None:
        """Soft delete user by id."""
        raise NotImplementedError

    @abstractmethod
    async def filter(self, filters: dict[str, Any]) -> list[T]:
        """Filter users by arbitrary criteria.

        Example: filter({"username": "foo"}), filter({"email": "bar", "is_active": True})
        Returns a list of users matching the criteria.
        """
        raise NotImplementedError
