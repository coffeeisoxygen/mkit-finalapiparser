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
from app.database.interfaces.intf_user import IUserRepo
from app.database.repositories.filter_helpers import (
    all_records_filter,
    inactive_filter,
    soft_deleted_filter,
    valid_record_filter,
)
from app.database.repositories.helpers import (
    pk_for_query,
    to_uuid,
    to_uuid_str,
)
from app.database.repositories.repo_audit import AuditMixinRepository
from app.mlogg import logger
from app.models.db_user import User
from app.schemas.sch_user import UserCreate, UserInDB, UserResponse, UserUpdate

settings = get_settings()
ADM_ID = uuid.UUID(str(settings.ADM_ID))


class SQLiteUserRepository(IUserRepo):
    async def activate(
        self, user_id: uuid.UUID | str, actor_id: uuid.UUID | str
    ) -> UserInDB:
        """Activate user (set is_active=True, is_deleted_flag=False).

        Args:
            user_id: PK (UUID or str).
            actor_id: Actor performing activation.

        Returns:
            UserInDB: Activated user.

        Raises:
            DataNotFoundError: If user not found.
        """
        user_obj = await self._get_user_or_raise(user_id)
        user_obj.is_active = True
        user_obj.is_deleted_flag = False
        user_obj.updated_by = to_uuid_str(actor_id)
        user_obj.updated_at = datetime.now().astimezone(UTC)
        await self._commit_or_flush(user_obj)
        return UserInDB.model_validate(user_obj)

    async def deactivate(
        self, user_id: uuid.UUID | str, actor_id: uuid.UUID | str
    ) -> UserInDB:
        """Deactivate user (set is_active=False, is_deleted_flag=False).

        Args:
            user_id: PK (UUID or str).
            actor_id: Actor performing deactivation.

        Returns:
            UserInDB: Deactivated user.

        Raises:
            DataNotFoundError: If user not found.
        """
        user_obj = await self._get_user_or_raise(user_id)
        user_obj.is_active = False
        user_obj.is_deleted_flag = False
        user_obj.updated_by = to_uuid_str(actor_id)
        user_obj.updated_at = datetime.now().astimezone(UTC)
        await self._commit_or_flush(user_obj)
        return UserInDB.model_validate(user_obj)

    """SQLite implementation of IUserRepo.

    All PK queries use pk_for_query for DB compatibility.
    Audit fields are always stored as string UUIDs.
    """

    def __init__(
        self,
        session: AsyncSession,
        autocommit: bool = True,
        audit_repo: AuditMixinRepository | None = None,
    ):
        """Initialize repository.

        Args:
            session: Async DB session.
            autocommit: If True, commit after each operation.
            audit_repo: Optional audit repo instance.
        """
        self.session = session
        self.autocommit = autocommit
        self.audit_repo = audit_repo or AuditMixinRepository(session, User)
        self.log = logger.bind(repo="SQLiteUserRepository")
        self.log.info(f"Initialized with autocommit={autocommit}")

    def _is_admin_id(self, user_id: uuid.UUID | str) -> bool:
        """Check if user_id is system admin.

        Args:
            user_id: PK (UUID or str).

        Returns:
            bool: True if admin.
        """
        return to_uuid(user_id) == ADM_ID

    async def _get_user_or_raise(self, user_id: uuid.UUID | str) -> User:
        """Get user by PK or raise DataNotFoundError.

        Args:
            user_id: PK (UUID or str).

        Returns:
            User: ORM user object.

        Raises:
            DataNotFoundError: If user not found.
        """
        user_id_pk = pk_for_query(user_id)
        user_obj = await self.session.get(User, user_id_pk)
        if not user_obj:
            self.log.error("Data not found", user_id=str(user_id_pk))
            raise DataNotFoundError(context={"user_id": str(user_id_pk)})
        return user_obj

    async def _check_duplicate_user(self, username: str, email: str) -> None:
        """Check for duplicate username or email.

        Args:
            username: Username to check.
            email: Email to check.

        Raises:
            DataDuplicationError: If duplicate found.
        """
        stmt = select(User).where((User.username == username) | (User.email == email))
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            self.log.error("Data duplication error", username=username, email=email)
            raise DataDuplicationError(context={"username": username, "email": email})

    async def _commit_or_flush(self, obj: User):
        """Commit or flush DB transaction.

        Args:
            obj: ORM object to refresh.

        Raises:
            DataGenericError: If commit/flush fails.
        """
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

    async def create(
        self,
        user: UserCreate,
        hashed_password: str,
        actor_id: uuid.UUID | str | None = None,
        is_superuser: bool = False,
    ) -> UserInDB:
        """Create new user.

        Args:
            user: UserCreate schema.
            hashed_password: Hashed password.
            actor_id: Actor performing creation.
            is_superuser: If True, user is superuser.

        Returns:
            UserInDB: Created user.

        Raises:
            ValueError: If actor_id missing.
            DataDuplicationError: If duplicate found.
        """
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

    async def get_by_id(
        self, user_id: uuid.UUID | str, include_deleted: bool = False
    ) -> UserInDB:
        """Get user by ID.

        Args:
            user_id: PK (UUID or str).
            include_deleted: If True, include soft-deleted users.

        Returns:
            UserInDB: User object.

        Raises:
            DataNotFoundError: If user not found.
        """
        user_id_pk = pk_for_query(user_id)
        if include_deleted:
            stmt = select(User).where(User.id == user_id_pk)
        else:
            stmt = select(User).where(User.id == user_id_pk, valid_record_filter(User))
        result = await self.session.execute(stmt)
        user_obj = result.scalar_one_or_none()
        if not user_obj:
            self.log.error("Data not found", method="get_by_id", user_id=user_id_pk)
            raise DataNotFoundError(context={"user_id": user_id_pk})
        return UserInDB.model_validate(user_obj)

    async def get_by_username(
        self, username: str, include_deleted: bool = False
    ) -> UserInDB:
        """Get user by username.

        Args:
            username: Username.
            include_deleted: If True, include soft-deleted users.

        Returns:
            UserInDB: User object.

        Raises:
            DataNotFoundError: If user not found.
        """
        if include_deleted:
            stmt = select(User).where(User.username == username)
        else:
            stmt = select(User).where(
                User.username == username, valid_record_filter(User)
            )
        result = await self.session.execute(stmt)
        user_obj = result.scalar_one_or_none()
        if not user_obj:
            self.log.error(
                "Data not found", method="get_by_username", username=username
            )
            raise DataNotFoundError(context={"username": username})
        return UserInDB.model_validate(user_obj)

    async def list_all(
        self, skip: int = 0, limit: int = 100, filter_type: str = "valid"
    ) -> list[UserResponse]:
        """List all users.

        Args:
            skip: Offset.
            limit: Max records.
            filter_type: "valid", "soft_deleted", "inactive", "all"

        Returns:
            list[UserResponse]: List of users.
        """
        if filter_type == "valid":
            filter_cond = valid_record_filter(User)
        elif filter_type == "soft_deleted":
            filter_cond = soft_deleted_filter(User)
        elif filter_type == "inactive":
            filter_cond = inactive_filter(User)
        elif filter_type == "all":
            filter_cond = all_records_filter(User)
        else:
            filter_cond = valid_record_filter(User)
        stmt = select(User).where(filter_cond).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        users = result.scalars().all()
        return [UserResponse.model_validate(u) for u in users]

    async def update(
        self,
        user_id: uuid.UUID | str,
        data: UserUpdate,
        actor_id: uuid.UUID | str | None = None,
    ) -> UserInDB:
        """Update user data.

        Args:
            user_id: PK (UUID or str).
            data: UserUpdate schema.
            actor_id: Actor performing update.

        Returns:
            UserInDB: Updated user.

        Raises:
            ValueError: If actor_id missing.
            DataNotFoundError: If user not found.
        """
        if actor_id is None:
            raise ValueError("actor_id is required for audit trail")

        user_id_uuid = to_uuid(user_id)
        actor_id_str = to_uuid_str(actor_id)
        user_obj = await self._get_user_or_raise(user_id_uuid)

        update_data = data.model_dump(exclude_unset=True)
        update_data.pop("password", None)  # NOTE: hashing handled in service

        for key, value in update_data.items():
            setattr(user_obj, key, value)
        user_obj.updated_by = actor_id_str

        self.log.info(
            "Updating user record",
            method="update",
            user_id=str(user_id_uuid),
            update_data=update_data,
        )

        await self._commit_or_flush(user_obj)
        return UserInDB.model_validate(user_obj)

    async def delete(self, user_id: uuid.UUID | str) -> None:
        """Hard delete user (hapus total).

        Args:
            user_id: PK (UUID or str).

        Raises:
            AdminCantDeleteError: If admin user.
            DataNotFoundError: If user not found.
            DataGenericError: If delete fails.
        """
        user_id_pk = pk_for_query(user_id)
        user_obj = await self._get_user_or_raise(user_id_pk)

        if self._is_admin_id(user_id_pk):
            self.log.error(
                "Attempt to delete system admin forbidden", user_id=str(user_id_pk)
            )
            raise AdminCantDeleteError(
                context={
                    "user_id": str(user_id_pk),
                    "error": "System admin cannot be deleted.",
                }
            )

        self.log.info("Deleting user record", user_id=str(user_id_pk))
        try:
            await self.session.delete(user_obj)
            if self.autocommit:
                await self.session.commit()
            else:
                await self.session.flush()
        except Exception as e:
            self.log.exception(
                "Exception during user delete", user_id=str(user_id_pk), error=str(e)
            )
            raise DataGenericError(
                "Failed to delete user record",
                cause=e,
                context={"user_id": str(user_id_pk)},
            ) from e

    async def soft_delete(
        self, user_id: uuid.UUID | str, actor_id: uuid.UUID | str
    ) -> None:
        """Soft delete user (pakai AuditMixin).

        Args:
            user_id: PK (UUID or str).
            actor_id: Actor performing delete.

        Raises:
            DataNotFoundError: If user not found.
            DataGenericError: If soft delete fails.
        """
        user_id_pk = pk_for_query(user_id)
        actor_id_pk = pk_for_query(actor_id)
        user_obj = await self._get_user_or_raise(user_id_pk)

        self.log.info(
            "Soft deleting user record",
            user_id=str(user_id_pk),
            actor_id=str(actor_id_pk),
        )
        try:
            await self.audit_repo.soft_delete(user_id_pk, actor_id_pk)
            user_obj.is_deleted_flag = True
            user_obj.deleted_by = to_uuid_str(actor_id_pk)
            user_obj.deleted_at = datetime.now().astimezone(UTC)

            if self.autocommit:
                await self.session.commit()
            else:
                await self.session.flush()
        except Exception as e:
            self.log.exception(
                "Exception during user soft delete",
                method="soft_delete",
                user_id=str(user_id_pk),
                error=str(e),
            )
            raise DataGenericError(
                "Failed to soft delete user record",
                cause=e,
                context={"user_id": str(user_id_pk)},
            ) from e
