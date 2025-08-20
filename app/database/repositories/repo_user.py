import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from typing import ClassVar

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
from app.database.repositories.helper_filters import (
    all_records_filter,
    inactive_filter,
    soft_deleted_filter,
    valid_record_filter,
)
from app.database.repositories.helpers_uuids import (
    pk_for_query,
    to_uuid_str,
)
from app.database.repositories.repo_audit import AuditMixinRepository
from app.mlogg import logger
from app.models.db_user import User
from app.schemas.sch_user import (
    AdminSeeder,
    UserCreate,
    UserFilterType,
    UserInDB,
    UserResponse,
    UserUpdateProfile,
)

settings = get_settings()
ADM_ID = uuid.UUID(str(settings.ADM_ID))


class SQLiteUserRepository(IUserRepo):
    # Static filter map for user listing
    FILTER_MAP: ClassVar[dict] = {
        UserFilterType.VALID: valid_record_filter(User),
        UserFilterType.SOFT_DELETED: soft_deleted_filter(User),
        UserFilterType.INACTIVE: inactive_filter(User),
        UserFilterType.ALL: all_records_filter(User),
    }
    """SQLite implementation of IUserRepo with audit support."""

    # --------------------
    # Initialization
    # --------------------
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

    # --------------------
    # Helper methods
    # --------------------
    def _is_admin_id(self, user_id: uuid.UUID | str) -> bool:
        """Check if user_id is system admin."""
        return pk_for_query(user_id) == pk_for_query(ADM_ID)

    def _actor_str(self, actor_id: uuid.UUID | str) -> str:
        """Convert actor_id to canonical string UUID."""
        return to_uuid_str(actor_id)

    async def _get_user_or_raise(
        self, user_id: uuid.UUID | str, include_deleted: bool = False
    ) -> User:
        """Get user by PK or raise DataNotFoundError."""
        user_id_pk = pk_for_query(user_id)
        stmt = (
            select(User).where(User.id == user_id_pk)
            if include_deleted
            else select(User).where(User.id == user_id_pk, valid_record_filter(User))
        )
        result = await self.session.execute(stmt)
        user_obj = result.scalar_one_or_none()
        if not user_obj:
            self.log.error("Data not found", user_id=user_id_pk)
            raise DataNotFoundError(context={"user_id": user_id_pk})
        return user_obj

    async def _get_user_by_username_or_raise(
        self, username: str, include_deleted: bool = False
    ) -> User:
        """Get user by username or raise DataNotFoundError."""
        stmt = (
            select(User).where(User.username == username)
            if include_deleted
            else select(User).where(
                User.username == username, valid_record_filter(User)
            )
        )
        result = await self.session.execute(stmt)
        user_obj = result.scalar_one_or_none()
        if not user_obj:
            self.log.error(
                "Data not found", method="get_by_username", username=username
            )
            raise DataNotFoundError(context={"username": username})
        return user_obj

    async def _check_duplicate_user(self, username: str, email: str) -> None:
        """Check for duplicate username or email."""
        stmt = select(User).where((User.username == username) | (User.email == email))
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            self.log.error("Data duplication error", username=username, email=email)
            raise DataDuplicationError(context={"username": username, "email": email})

    async def _commit_or_flush(self, obj: User):
        """Commit or flush DB transaction."""
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

    async def _set_active_flag(
        self, user_id: uuid.UUID | str, actor_id: uuid.UUID | str, active: bool
    ) -> UserInDB:
        """Set user active/inactive status."""
        user_obj = await self._get_user_or_raise(user_id)
        user_obj.is_active = active
        user_obj.is_deleted_flag = False
        user_obj.updated_by = self._actor_str(actor_id)
        user_obj.updated_at = datetime.now().astimezone(UTC)
        await self._commit_or_flush(user_obj)
        return UserInDB.model_validate(user_obj)

    # --------------------
    # Admin / Seeder methods
    # --------------------
    async def create_admin_with_id(
        self,
        admin: AdminSeeder,
        actor_id: uuid.UUID | str | None = None,
        hasher: Callable[[str], str] | None = None,
    ) -> UserInDB:
        """Create admin user with explicit ID (for seeding)."""
        if actor_id is None:
            raise ValueError("actor_id is required for audit trail")
        actor_id_str = to_uuid_str(actor_id)
        hasher = hasher or (lambda x: x)

        await self._check_duplicate_user(admin.username, admin.email)

        hashed_password = hasher(admin.password)
        try:
            new_admin = User(
                id=str(admin.id),
                username=admin.username,
                email=admin.email,
                full_name=admin.full_name,
                hashed_password=hashed_password,
                is_superuser=admin.is_superuser,
                is_active=admin.is_active,
                is_deleted_flag=admin.is_deleted,
                created_by=actor_id_str,
            )
            self.session.add(new_admin)
            await self._commit_or_flush(new_admin)
            self.log.info(
                "Admin user seeded", username=admin.username, actor_id=actor_id_str
            )
            return UserInDB.model_validate(new_admin)
        except Exception as e:
            self.log.exception(
                "Failed to seed admin user", username=admin.username, error=str(e)
            )
            raise DataGenericError("Failed to seed admin user", cause=e) from e

    # --------------------
    # CRUD operations
    # --------------------
    async def create(
        self,
        user: UserCreate,
        hashed_password: str,
        actor_id: uuid.UUID | str | None = None,
        is_superuser: bool = False,
    ) -> UserInDB:
        """Create new user."""
        if actor_id is None:
            raise ValueError("actor_id is required for audit trail")
        actor_id_str = to_uuid_str(actor_id)

        await self._check_duplicate_user(user.username, user.email)

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
        """Get user by ID."""
        user_obj = await self._get_user_or_raise(
            user_id, include_deleted=include_deleted
        )
        return UserInDB.model_validate(user_obj)

    async def get_by_username(
        self, username: str, include_deleted: bool = False
    ) -> UserInDB:
        """Get user by username."""
        user_obj = await self._get_user_by_username_or_raise(
            username, include_deleted=include_deleted
        )
        return UserInDB.model_validate(user_obj)

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filter_type: UserFilterType = UserFilterType.VALID,
    ) -> list[UserResponse]:
        """List all users."""
        filter_cond = self.FILTER_MAP.get(filter_type, valid_record_filter(User))
        stmt = select(User).where(filter_cond).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        users = result.scalars().all()
        return [UserResponse.model_validate(u) for u in users]

    async def update(
        self,
        user_id: uuid.UUID | str,
        data: UserUpdateProfile,
        actor_id: uuid.UUID | str | None = None,
    ) -> UserInDB:
        """Update user profile fields only. Logs warning if password field is present."""
        if actor_id is None:
            raise ValueError("actor_id is required for audit trail")

        user_obj = await self._get_user_or_raise(pk_for_query(user_id))
        update_data = data.model_dump(exclude_unset=True)
        if "password" in update_data:
            self.log.warning(
                "Password field present in update_data, ignored.",
                user_id=pk_for_query(user_id),
                update_data=update_data,
            )
            update_data.pop("password")
        # Only update allowed fields (username, email, full_name)
        allowed_fields = {"username", "email", "full_name"}
        for key, value in update_data.items():
            if key in allowed_fields:
                setattr(user_obj, key, value)
            else:
                self.log.warning(
                    f"Attempt to update disallowed field '{key}' ignored.",
                    user_id=pk_for_query(user_id),
                )
        user_obj.updated_by = to_uuid_str(actor_id)
        await self._commit_or_flush(user_obj)
        self.log.info(
            "Updating user record",
            method="update",
            user_id=pk_for_query(user_id),
            update_data=update_data,
        )
        return UserInDB.model_validate(user_obj)

    async def delete(self, user_id: uuid.UUID | str) -> None:
        """Hard delete user."""
        user_id_pk = pk_for_query(user_id)
        user_obj = await self._get_user_or_raise(user_id_pk)
        if self._is_admin_id(user_id_pk):
            self.log.error(
                "Attempt to delete system admin forbidden", user_id=user_id_pk
            )
            raise AdminCantDeleteError(
                context={
                    "user_id": user_id_pk,
                    "error": "System admin cannot be deleted.",
                }
            )
        self.log.info("Deleting user record", user_id=user_id_pk)
        try:
            await self.session.delete(user_obj)
            if self.autocommit:
                await self.session.commit()
            else:
                await self.session.flush()
        except Exception as e:
            self.log.exception(
                "Exception during user delete", user_id=user_id_pk, error=str(e)
            )
            raise DataGenericError(
                "Failed to delete user record",
                cause=e,
                context={"user_id": user_id_pk},
            ) from e

    # --------------------
    # Soft delete / activate-deactivate
    # --------------------
    async def soft_delete(
        self, user_id: uuid.UUID | str, actor_id: uuid.UUID | str
    ) -> None:
        """Soft delete user (pakai AuditMixin)."""
        user_id_pk = pk_for_query(user_id)
        actor_id_pk = pk_for_query(actor_id)
        try:
            await self.audit_repo.soft_delete(user_id_pk, actor_id_pk)
        except Exception as e:
            self.log.exception(
                "Exception during user soft delete",
                method="soft_delete",
                user_id=user_id_pk,
                error=str(e),
            )
            raise DataGenericError(
                "Failed to soft delete user record",
                cause=e,
                context={"user_id": user_id_pk},
            ) from e

    async def activate(
        self, user_id: uuid.UUID | str, actor_id: uuid.UUID | str
    ) -> UserInDB:
        """Activate user (set is_active=True, is_deleted_flag=False)."""
        return await self._set_active_flag(user_id, actor_id, True)

    async def deactivate(
        self, user_id: uuid.UUID | str, actor_id: uuid.UUID | str
    ) -> UserInDB:
        """Deactivate user (set is_active=False, is_deleted_flag=False)."""
        return await self._set_active_flag(user_id, actor_id, False)
