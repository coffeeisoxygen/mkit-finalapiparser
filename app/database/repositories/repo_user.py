from pydantic_extra_types.ulid import ULID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.custom.exceptions.cst_exceptions import DataDuplicationError, DataNotFoundError
from app.database.core import valid_record_filter
from app.database.repositories.repo_audit import AuditMixinRepository
from app.interfaces.intf_user import IUserRepo
from app.mlogg import logger
from app.models.db_user import User
from app.schemas.sch_user import UserCreate, UserInDB, UserResponse, UserUpdate


def ensure_ulid(val: ULID | str | None) -> ULID | None:
    """Convert value to ULID or str if needed, else None."""
    if val is None:
        return None
    if isinstance(val, ULID):
        return val
    # Accept int or str, return as str for DB audit fields
    return str(val)


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
        self.audit_repo = audit_repo or AuditMixinRepository()
        self.log = logger.bind(repo="SQLiteUserRepository")
        self.log.info(f"Initialized with autocommit={autocommit}")

        # NOTE: Service / caller wajib commit / rollback
        # kalau autocommit=False, maka repo hanya flush, tidak commit

    async def _check_duplicate_user(self, username: str, email: str) -> None:
        stmt = select(User).where((User.username == username) | (User.email == email))
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            self.log.error("Data duplication error", username=username, email=email)
            raise DataDuplicationError(context={"username": username, "email": email})

    async def create(
        self,
        user: UserCreate,
        hashed_password: str,
        actor_id: ULID | str | None = None,
        is_superuser: bool = False,
    ) -> UserInDB:
        await self._check_duplicate_user(user.username, user.email)
        new_user = User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=hashed_password,
            is_superuser=is_superuser,
            created_by=ensure_ulid(actor_id),
        )
        self.session.add(new_user)
        if self.autocommit:
            await self.session.commit()
            await self.session.refresh(new_user)
        else:
            await self.session.flush()
        self.log.info("User created", username=user.username, actor_id=actor_id)
        return UserInDB.model_validate(new_user)

    async def get_by_id(self, user_id: ULID | str) -> UserInDB:
        stmt = select(User).where(User.id == user_id, valid_record_filter(User))
        result = await self.session.execute(stmt)
        user_obj = result.scalar_one_or_none()
        if not user_obj:
            self.log.error("Data not found", method="get_by_id", user_id=user_id)
            raise DataNotFoundError(context={"user_id": user_id})
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
        self, user_id: ULID | str, data: UserUpdate, actor_id: ULID | str | None = None
    ) -> UserInDB:
        user_obj = await self.session.get(User, user_id)
        if not user_obj:
            self.log.error(
                "Data not found for update",
                method="update",
                user_id=user_id,
                data=data.model_dump(),
            )
            raise DataNotFoundError(
                context={"user_id": user_id, "data": data.model_dump()}
            )
        update_data = data.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data.pop("password")  # NOTE: hashing handled in service
        for key, value in update_data.items():
            setattr(user_obj, key, value)
        # Ensure actor_id is ULID object
        user_obj.updated_by = ensure_ulid(actor_id)
        self.log.info(
            "Updating user record",
            method="update",
            user_id=user_id,
            update_data=update_data,
        )
        try:
            if self.autocommit:
                await self.session.commit()
                await self.session.refresh(user_obj)
            else:
                await self.session.flush()
                await self.session.refresh(user_obj)
        except Exception as e:
            self.log.exception(
                "Exception during user update", user_id=user_id, error=str(e)
            )
            raise
        return UserInDB.model_validate(user_obj)

    async def delete(self, user_id: ULID | str) -> None:
        user_obj = await self.session.get(User, user_id)
        if not user_obj:
            self.log.error("Data not found for delete", user_id=user_id)
            raise DataNotFoundError(context={"user_id": user_id})
        self.log.info("Deleting user record", user_id=user_id)
        try:
            await self.session.delete(user_obj)
            if self.autocommit:
                await self.session.commit()
            else:
                await self.session.flush()
        except Exception as e:
            self.log.exception(
                "Exception during user delete", user_id=user_id, error=str(e)
            )
            raise

    async def soft_delete(self, user_id: ULID | str, actor_id: ULID | str) -> None:
        user_obj = await self.session.get(User, user_id)
        if not user_obj:
            self.log.error(
                "Data not found for soft delete", method="soft_delete", user_id=user_id
            )
            raise DataNotFoundError(context={"user_id": user_id, "actor_id": actor_id})
        self.log.info("Soft deleting user record", user_id=user_id, actor_id=actor_id)
        try:
            # Delegasi ke repo audit
            await self.audit_repo.soft_delete(user_id, ensure_ulid(actor_id))
            user_obj.is_deleted_flag = True
            user_obj.deleted_by = ensure_ulid(actor_id)
            if self.autocommit:
                await self.session.commit()
            else:
                await self.session.flush()
        except Exception as e:
            self.log.exception(
                "Exception during user soft delete",
                method="soft_delete",
                user_id=user_id,
                error=str(e),
            )
            raise
