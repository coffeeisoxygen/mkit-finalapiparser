from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.custom.exceptions.cst_exceptions import DataDuplicationError, DataNotFoundError
from app.interfaces.intf_user import IUserRepo
from app.mlogg import logger
from app.models.db_user import User
from app.schemas.sch_user import UserCreate, UserInDB, UserPublic, UserUpdate


class SQLiteUserRepository(IUserRepo):
    """SQLite implementation of IUserRepo."""

    def __init__(self, session: AsyncSession, autocommit: bool = True):
        """Initialize repository.

        Args:
            session: AsyncSession instance.
            autocommit: If True, repo will commit after each write op. If False, caller/UoW must commit.
        """
        self.session = session
        self.autocommit = autocommit
        logger.bind(repo="SQLiteUserRepository").info(
            "SQLiteUserRepository initialized with autocommit=%s", autocommit
        )

    async def _check_duplicate_user(self, username: str, email: str) -> None:
        """Helper to check for duplicate username or email.

        Raises:
            DataDuplicationError: If a user with the same username or email exists.
        """
        stmt = select(User).where((User.username == username) | (User.email == email))
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            logger.bind(
                method="_check_duplicate_user", username=username, email=email
            ).exception("Data duplication error")
            raise DataDuplicationError(context={"username": username, "email": email})

    async def create(
        self, user: UserCreate, hashed_password: str, actor_id: int | None = None
    ) -> UserInDB:
        """Create user. Caller is responsible for commit/rollback if autocommit=False."""
        await self._check_duplicate_user(user.username, user.email)

        new_user = User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=hashed_password,
            is_superuser=False,
            created_by=actor_id,
        )
        self.session.add(new_user)
        if self.autocommit:
            await self.session.commit()
            await self.session.refresh(new_user)
        else:
            await self.session.flush()
        return UserInDB.model_validate(new_user)

    async def get_by_id(self, user_id: int) -> UserInDB | None:
        """Get by id database. Raises DataNotFoundError if not found."""
        user_obj = await self.session.get(User, user_id)
        if not user_obj:
            logger.bind(method="get_by_id", user_id=user_id).exception("Data not found")
            raise DataNotFoundError(context={"user_id": user_id})
        return UserInDB.model_validate(user_obj)

    async def get_by_username(self, username: str) -> UserInDB | None:
        """Get by username. Raises DataNotFoundError if not found."""
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        user_obj = result.scalar_one_or_none()
        if not user_obj:
            logger.bind(method="get_by_username", username=username).exception(
                "Data not found"
            )
            raise DataNotFoundError(context={"username": username})
        return UserInDB.model_validate(user_obj)

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[UserPublic]:
        """Returns a list of all users."""
        stmt = select(User).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        users = result.scalars().all()
        return [UserPublic.model_validate(u) for u in users]

    async def update(
        self, user_id: int, data: UserUpdate, actor_id: int | None = None
    ) -> UserInDB | None:
        """Update user data. Caller is responsible for commit/rollback if autocommit=False."""
        user_obj = await self.session.get(User, user_id)
        if not user_obj:
            return None

        update_data = data.model_dump(exclude_unset=True)
        if "password" in update_data:
            # NOTE: hashed_password harus dihandle di service
            update_data.pop("password")

        for key, value in update_data.items():
            setattr(user_obj, key, value)

        user_obj.updated_by = actor_id
        if self.autocommit:
            await self.session.commit()
            await self.session.refresh(user_obj)
        else:
            await self.session.flush()
        return UserInDB.model_validate(user_obj)

    async def delete(self, user_id: int) -> None:
        """Hard delete user. Caller is responsible for commit/rollback if autocommit=False."""
        user_obj = await self.session.get(User, user_id)
        if user_obj:
            await self.session.delete(user_obj)
            if self.autocommit:
                await self.session.commit()
            else:
                await self.session.flush()

    async def soft_delete(self, user_id: int, actor_id: int) -> None:
        """Soft delete user (pakai AuditMixin). Caller is responsible for commit/rollback if autocommit=False."""
        user_obj = await self.session.get(User, user_id)
        if user_obj:
            user_obj.soft_delete(actor_id)
            if self.autocommit:
                await self.session.commit()
            else:
                await self.session.flush()
