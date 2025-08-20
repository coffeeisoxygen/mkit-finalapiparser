import uuid
from abc import ABC, abstractmethod

from app.schemas.sch_user import UserCreate, UserInDB, UserResponse, UserUpdate


# TODO: kalau Udah Mulai Pake Database Postgres dan lain lain , baru refactor ya
class IUserRepo(ABC):
    """Interface untuk operasi repository User."""

    @abstractmethod
    async def create(
        self,
        user: UserCreate,
        hashed_password: str,
        actor_id: uuid.UUID | str | None = None,
    ) -> UserInDB:
        """Buat user baru. Return UserInDB."""
        pass

    @abstractmethod
    async def get_by_id(self, user_id: uuid.UUID | str) -> UserInDB | None:
        """Ambil user by ID. Accepts UUID or string UUID for compatibility with DB drivers."""
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> UserInDB | None:
        """Ambil user by username."""
        pass

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> list[UserResponse]:
        """List semua user (public)."""
        pass

    @abstractmethod
    async def update(
        self,
        user_id: uuid.UUID | str,
        data: UserUpdate,
        actor_id: uuid.UUID | str | None = None,
    ) -> UserInDB | None:
        """Update data user. Accepts UUID or string UUID for compatibility with DB drivers."""
        pass

    @abstractmethod
    async def delete(self, user_id: uuid.UUID | str) -> None:
        """Hard delete user (hapus total). Accepts UUID or string UUID for compatibility with DB drivers."""
        pass

    @abstractmethod
    async def soft_delete(
        self, user_id: uuid.UUID | str, actor_id: uuid.UUID | str
    ) -> None:
        """Soft delete user (pakai AuditMixin). Accepts UUID or string UUID for compatibility with DB drivers."""
        pass
