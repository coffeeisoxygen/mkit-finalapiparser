from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.interfaces.intf_user import IUserRepo
from app.models.db_user import User
from app.schemas.sch_user import UserCreate, UserInDB, UserPublic, UserUpdate


class SQLiteUserRepository(IUserRepo):
    """SQLite implementation of IUserRepo."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self, user: UserCreate, hashed_password: str, actor_id: int | None = None
    ) -> UserInDB:
        """Creating user."""
        new_user = User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=hashed_password,
            is_superuser=False,
            created_by=actor_id,
        )
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return UserInDB.model_validate(new_user)

    async def get_by_id(self, user_id: int) -> UserInDB | None:
        """Get by id database."""
        user_obj = await self.session.get(User, user_id)
        return UserInDB.model_validate(user_obj) if user_obj else None

    async def get_by_username(self, username: str) -> UserInDB | None:
        """Get by username."""
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        user_obj = result.scalar_one_or_none()
        return UserInDB.model_validate(user_obj) if user_obj else None

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[UserPublic]:
        """Returns a list of all users."""
        stmt = select(User).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        users = result.scalars().all()
        return [UserPublic.model_validate(u) for u in users]

    async def update(
        self, user_id: int, data: UserUpdate, actor_id: int | None = None
    ) -> UserInDB | None:
        """Update user data."""
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
        await self.session.commit()
        await self.session.refresh(user_obj)
        return UserInDB.model_validate(user_obj)

    async def delete(self, user_id: int) -> None:
        """Hard delete user."""
        user_obj = await self.session.get(User, user_id)
        if user_obj:
            await self.session.delete(user_obj)
            await self.session.commit()

    async def soft_delete(self, user_id: int, actor_id: int) -> None:
        """Soft delete user (pakai AuditMixin)."""
        user_obj = await self.session.get(User, user_id)
        if user_obj:
            user_obj.soft_delete(actor_id)
            await self.session.commit()
