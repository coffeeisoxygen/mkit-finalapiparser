"""Service layer for user CRUD operations."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.core.uow import UnitOfWork
from app.database.repositories.repo_user import SQLiteUserRepository
from app.mlogg import logger
from app.mlogg.utils import logger_wraps
from app.schemas.sch_user import (
    UserCreate,
    UserFilterType,
    UserInDB,
    UserResponse,
    UserUpdate,
)
from app.service.security.srv_hasher import HasherService


class UserCrudService:
    """Service for user CRUD, using UoW and repository."""

    def __init__(self, session: AsyncSession, hasher: HasherService | None = None):
        self.session = session
        self.hasher = hasher or HasherService()
        self.repo = SQLiteUserRepository(session, autocommit=False)
        self.log = logger.bind(service="UserCrudService")

    @logger_wraps(entry=True, exit=True, level="INFO")
    async def create_user(
        self,
        user: UserCreate,
        actor_id: uuid.UUID | str | None = None,
    ) -> UserInDB:
        """Create user with password hashing."""
        hashed_password = self.hasher.hash_value(user.password)
        async with UnitOfWork(self.session) as uow:
            new_user = await self.repo.create(user, hashed_password, actor_id)
            await uow.commit()
            self.log.info(
                "User created via service", username=user.username, actor_id=actor_id
            )
            return new_user

    @logger_wraps(entry=True, exit=True, level="INFO")
    async def get_user_by_id(self, user_id: uuid.UUID | str) -> UserInDB:
        return await self.repo.get_by_id(user_id)

    @logger_wraps(entry=True, exit=True, level="INFO")
    async def get_user_by_username(self, username: str) -> UserInDB:
        return await self.repo.get_by_username(username)

    @logger_wraps(entry=True, exit=True, level="INFO")
    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        filter_type: UserFilterType | None = None,
    ) -> list[UserResponse]:
        """List users with dynamic filter type."""
        filter_type = filter_type or UserFilterType.VALID
        return await self.repo.list_all(skip=skip, limit=limit, filter_type=filter_type)

    @logger_wraps(entry=True, exit=True, level="INFO")
    async def update_user(
        self,
        user_id: uuid.UUID | str,
        data: UserUpdate,
        actor_id: uuid.UUID | str | None = None,
    ) -> UserInDB:
        """Update user, hash password if present."""
        update_data = data.model_dump(exclude_unset=True)
        if update_data.get("password"):
            update_data["password"] = self.hasher.hash_value(update_data["password"])
        update_schema = UserUpdate(**update_data)
        async with UnitOfWork(self.session) as uow:
            updated_user = await self.repo.update(user_id, update_schema, actor_id)
            await uow.commit()
            self.log.info(
                "User updated via service", user_id=user_id, actor_id=actor_id
            )
            return updated_user

    @logger_wraps(entry=True, exit=True, level="INFO")
    async def delete_user(self, user_id: uuid.UUID | str) -> None:
        async with UnitOfWork(self.session) as uow:
            await self.repo.delete(user_id)
            await uow.commit()
            self.log.info("User deleted via service", user_id=user_id)

    @logger_wraps(entry=True, exit=True, level="INFO")
    async def soft_delete_user(
        self, user_id: uuid.UUID | str, actor_id: uuid.UUID | str
    ) -> None:
        async with UnitOfWork(self.session) as uow:
            await self.repo.soft_delete(user_id, actor_id)
            await uow.commit()
            self.log.info(
                "User soft deleted via service", user_id=user_id, actor_id=actor_id
            )
