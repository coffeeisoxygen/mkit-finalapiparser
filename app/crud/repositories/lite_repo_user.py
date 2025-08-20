"""Module for SQLite-based user repository implementation.

This module provides the LiteUserRepo class, a concrete implementation of
IUserRepo for managing User entities using SQLAlchemy's AsyncSession with
SQLite as the backend. It supports CRUD operations, soft deletion, and
filtering users by arbitrary criteria.

Note:
    - All database changes are flushed but not committed; transaction
      management is handled by the Unit of Work (UOW) or service layer.
    - Exceptions related to data integrity are raised as DataIntegrityError.
"""

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.interfaces import IUserRepo
from app.crud.repositories.repo_helper import to_uuid_str
from app.custom.exceptions import DataIntegrityError
from app.models import User


class LiteUserRepo(IUserRepo[User]):
    """SQLite repository for User entities using SQLAlchemy AsyncSession.

    This class implements the IUserRepo interface, providing asynchronous
    CRUD operations, soft deletion, and filtering for User objects.

    Args:
        session (AsyncSession): The SQLAlchemy async session for DB operations.

    Note:
        - Only flushes changes; commit/rollback is managed externally.
        - Raises DataIntegrityError on DB integrity issues.
    """

    def __init__(self, session: AsyncSession):
        """Initialize LiteUserRepo with an AsyncSession.

        Args:
            session (AsyncSession): The SQLAlchemy async session.
        """
        self.session = session

    async def create(self, data: dict[str, Any]) -> User:
        """Create a new user and flush to the database.

        Args:
            data (dict[str, Any]): Dictionary of user attributes.

        Returns:
            User: The newly created User object.

        Raises:
            DataIntegrityError: If user creation fails due to DB error.

        Note:
            Commit is handled by the UOW/service layer.
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
        """Retrieve a user by their unique ID.

        Args:
            id (str | uuid.UUID): The user's ID.

        Returns:
            User | None: The User object if found, else None.
        """
        stmt = select(User).where(User.id == to_uuid_str(id))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> list[User]:
        """Retrieve all users from the database.

        Returns:
            list[User]: List of all User objects.
        """
        stmt = select(User)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, id: str | uuid.UUID, updates: dict[str, Any]) -> User:
        """Update user fields and flush changes to the database.

        Args:
            id (str | uuid.UUID): The user's ID.
            updates (dict[str, Any]): Fields to update.

        Returns:
            User: The updated User object.

        Raises:
            DataIntegrityError: If user not found or update fails.

        Note:
            Commit is handled by the UOW/service layer.
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
        """Soft delete a user by setting the deleted_at field.

        Args:
            id (str | uuid.UUID): The user's ID.

        Raises:
            DataIntegrityError: If user not found or deletion fails.

        Note:
            Commit is handled by the UOW/service layer.
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
        """Filter users by arbitrary criteria.

        Args:
            filters (dict[str, Any]): Dictionary of field-value pairs to filter.

        Returns:
            list[User]: List of User objects matching the filters.
        """
        stmt = select(User)
        for key, value in filters.items():
            column = getattr(User, key, None)
            if column is not None:
                stmt = stmt.where(column == value)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
