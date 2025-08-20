"""concrete implementation of sqlite repositories for user."""

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.interfaces import IUserRepo
from app.crud.repositories.repo_helper import to_uuid_str
from app.custom.exceptions import DataIntegrityError
from app.models import User


class LiteUserRepo(IUserRepo[User]):
    """Concrete implementation of IUserRepo for SQLite using SQLAlchemy AsyncSession.

    NOTE: This repository only flushes changes. Commit/rollback is managed by the UOW/service layer.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: dict[str, Any]) -> User:
        """Create a new user and flush to DB.
        #NOTE: Commit is handled by UOW/service layer.
        """
        user = User(**data)
        self.session.add(user)
        try:
            await self.session.flush()
        except Exception as exc:
            raise DataIntegrityError(f"Failed to create user: {exc}") from exc
        await self.session.refresh(user)
        return user

    async def get_by_id(self, id: str | uuid.UUID) -> User | None:
        """Get a user by ID."""
        stmt = select(User).where(User.id == to_uuid_str(id))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> list[User]:
        """Get all users."""
        stmt = select(User)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, id: str | uuid.UUID, updates: dict[str, Any]) -> User:
        """Update user fields and flush to DB.
        #NOTE: Commit is handled by UOW/service layer.
        """
        stmt = select(User).where(User.id == to_uuid_str(id))
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise DataIntegrityError("User not found.")
        for key, value in updates.items():
            setattr(user, key, value)
        try:
            await self.session.flush()
        except Exception as exc:
            raise DataIntegrityError(f"Failed to update user: {exc}") from exc
        await self.session.refresh(user)
        return user

    async def soft_delete(self, id: str | uuid.UUID) -> None:
        """Soft delete a user (set deleted_at) and flush to DB.
        #NOTE: Commit is handled by UOW/service layer.
        """
        stmt = select(User).where(User.id == to_uuid_str(id))
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise DataIntegrityError("User not found.")
        user.deleted_at = user.deleted_at or user.updated_at  # Mark as deleted
        try:
            await self.session.flush()
        except Exception as exc:
            raise DataIntegrityError(f"Failed to soft delete user: {exc}") from exc

    async def filter(self, filters: dict[str, Any]) -> list[User]:
        """Filter users by arbitrary criteria."""
        stmt = select(User)
        for key, value in filters.items():
            column = getattr(User, key, None)
            if column is not None:
                stmt = stmt.where(column == value)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
