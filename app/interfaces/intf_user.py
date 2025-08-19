"""contains user-related interfaces."""

from abc import ABC, abstractmethod

from app.schemas.sch_user import UserInDB


class IUserRepo(ABC):
    """Interface for user repository operations."""

    @abstractmethod
    async def get_by_id(self, user_id: int) -> UserInDB | None:
        """Retrieve a user by their ID."""
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> UserInDB | None:
        """Retrieve a user by their username."""
        pass

    @abstractmethod
    async def create(self, user_data: UserInDB) -> UserInDB:
        """Create a new user with the provided data."""
        pass

    @abstractmethod
    async def update(self, user_id: int, user_data: UserInDB) -> UserInDB | None:
        """Update an existing user's data."""
        pass

    @abstractmethod
    async def delete(self, user_id: int) -> None:
        """Delete a user by their ID."""
        pass
