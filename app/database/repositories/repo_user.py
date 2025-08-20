import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.custom.exceptions.cst_exceptions import (
    AdminCantDeleteError,
    DataDuplicationError,
    DataGenericError,
    DataNotFoundError,
)
from app.database.repositories.helpers import to_uuid, to_uuid_str, valid_record_filter
from app.database.repositories.repo_audit import AuditMixinRepository
from app.interfaces.intf_user import IUserRepo
from app.mlogg import logger
from app.models.db_user import User
from app.schemas.sch_user import UserCreate, UserInDB, UserResponse, UserUpdate

settings = get_settings()
ADM_ID = uuid.UUID(str(settings.ADM_ID))


class SQLiteUserRepository(IUserRepo):
    """SQLite implementation of IUserRepo."""

    def __init__(
        self,
        session: AsyncSession,
        autocommit: bool = True,
        audit_repo: AuditMixinRepository | None = None,
    ):
        self.session = session
        self.autocommit = autocommit
        self.audit_repo = audit_repo or AuditMixinRepository(session, User)
        self.log = logger.bind(repo="SQLiteUserRepository")
        self.log.info(f"Initialized with autocommit={autocommit}")

    # ----------------- Helper Methods -----------------

    # Use global helpers for UUID conversion

    def _is_admin_id(self, user_id: uuid.UUID | str) -> bool:
        return to_uuid(user_id) == ADM_ID

    async def _get_user_or_raise(self, user_id: uuid.UUID | str) -> User:
        user_id_str = to_uuid_str(user_id)
        user_obj = await self.session.get(User, user_id_str)
        if not user_obj:
            self.log.error("Data not found", user_id=user_id_str)
            raise DataNotFoundError(context={"user_id": user_id_str})
        return user_obj

    async def _check_duplicate_user(self, username: str, email: str) -> None:
        stmt = select(User).where((User.username == username) | (User.email == email))
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            self.log.error("Data duplication error", username=username, email=email)
            raise DataDuplicationError(context={"username": username, "email": email})

    async def _commit_or_flush(self, obj: User):
        try:
            if self.autocommit:
                await self.session.commit()
                await self.session.refresh(obj)
            else:
                await self.session.flush()
                await self.session.refresh(obj)
        except Exception as e:
            self.log.exception("Database commit/flush failed", error=str(e))
            raise DataGenericError("Failed to commit/flush transaction", cause=e) from e

    # ----------------- CRUD Methods -----------------
    async def create(
        self,
        user: UserCreate,
        hashed_password: str,
        actor_id: uuid.UUID | str | None = None,
        is_superuser: bool = False,
    ) -> UserInDB:
        if actor_id is None:
            raise ValueError("actor_id is required for audit trail")
        actor_id_str = to_uuid_str(actor_id)

        await self._check_duplicate_user(user.username, user.email)

        self.log.debug(
            "Creating user with audit fields",
            username=user.username,
            actor_id=actor_id_str,
            created_by=actor_id_str,
        )

        new_user = User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=hashed_password,
            is_superuser=is_superuser,
            created_by=actor_id_str,
        )
        self.session.add(new_user)
        await self._commit_or_flush(new_user)

        self.log.info("User created", username=user.username, actor_id=actor_id_str)
        return UserInDB.model_validate(new_user)

    async def get_by_id(self, user_id: uuid.UUID | str) -> UserInDB:
        user_id_str = to_uuid_str(user_id)
        stmt = select(User).where(User.id == user_id_str, valid_record_filter(User))
        result = await self.session.execute(stmt)
        user_obj = result.scalar_one_or_none()
        if not user_obj:
            self.log.error("Data not found", method="get_by_id", user_id=user_id_str)
            raise DataNotFoundError(context={"user_id": user_id_str})
        return UserInDB.model_validate(user_obj)

    async def get_by_username(self, username: str) -> UserInDB:
        stmt = select(User).where(User.username == username, valid_record_filter(User))
        result = await self.session.execute(stmt)
        user_obj = result.scalar_one_or_none()
        if not user_obj:
            self.log.error(
                "Data not found", method="get_by_username", username=username
            )
            raise DataNotFoundError(context={"username": username})
        return UserInDB.model_validate(user_obj)

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[UserResponse]:
        stmt = select(User).where(valid_record_filter(User)).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        users = result.scalars().all()
        return [UserResponse.model_validate(u) for u in users]

    async def update(
        self,
        user_id: uuid.UUID | str,
        data: UserUpdate,
        actor_id: uuid.UUID | str | None = None,
    ) -> UserInDB:
        if actor_id is None:
            raise ValueError("actor_id is required for audit trail")

        user_id_str = to_uuid_str(user_id)
        actor_id_str = to_uuid_str(actor_id)
        user_obj = await self._get_user_or_raise(user_id_str)

        update_data = data.model_dump(exclude_unset=True)
        update_data.pop("password", None)  # NOTE: hashing handled in service

        for key, value in update_data.items():
            setattr(user_obj, key, value)
        user_obj.updated_by = actor_id_str

        self.log.info(
            "Updating user record",
            method="update",
            user_id=user_id_str,
            update_data=update_data,
        )

        await self._commit_or_flush(user_obj)
        return UserInDB.model_validate(user_obj)

    async def delete(self, user_id: uuid.UUID | str) -> None:
        user_id_str = to_uuid_str(user_id)
        user_obj = await self._get_user_or_raise(user_id_str)

        if self._is_admin_id(user_id_str):
            self.log.error(
                "Attempt to delete system admin forbidden", user_id=user_id_str
            )
            raise AdminCantDeleteError(
                context={
                    "user_id": user_id_str,
                    "error": "System admin cannot be deleted.",
                }
            )

        self.log.info("Deleting user record", user_id=user_id_str)
        try:
            await self.session.delete(user_obj)
            if self.autocommit:
                await self.session.commit()
            else:
                await self.session.flush()
        except Exception as e:
            self.log.exception(
                "Exception during user delete", user_id=user_id_str, error=str(e)
            )
            raise DataGenericError(
                "Failed to delete user record",
                cause=e,
                context={"user_id": user_id_str},
            ) from e

    async def soft_delete(
        self, user_id: uuid.UUID | str, actor_id: uuid.UUID | str
    ) -> None:
        user_id_str = to_uuid_str(user_id)
        actor_id_str = to_uuid_str(actor_id)
        user_obj = await self._get_user_or_raise(user_id_str)

        self.log.info(
            "Soft deleting user record", user_id=user_id_str, actor_id=actor_id_str
        )
        try:
            await self.audit_repo.soft_delete(
                to_uuid(user_id_str), to_uuid(actor_id_str)
            )
            user_obj.is_deleted_flag = True
            user_obj.deleted_by = actor_id_str
            user_obj.deleted_at = datetime.now().astimezone(UTC)

            if self.autocommit:
                await self.session.commit()
            else:
                await self.session.flush()
        except Exception as e:
            self.log.exception(
                "Exception during user soft delete",
                method="soft_delete",
                user_id=user_id_str,
                error=str(e),
            )
            raise DataGenericError(
                "Failed to soft delete user record",
                cause=e,
                context={"user_id": user_id_str},
            ) from e
