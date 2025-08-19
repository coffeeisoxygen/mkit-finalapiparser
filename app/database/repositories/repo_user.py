"""repository for user."""

from sqlalchemy import select

from app.database.core import session
from app.interfaces.intf_user import IUserRepo
from app.models.db_user import User
from app.schemas.sch_user import UserInDB


class SQLiteUserRepository(IUserRepo):
    """SQLite implementation of the user repository interface."""

    def __init__(self, session: session.AsyncSession):
        self.session = session

    async def create(self, user_data: UserInDB) -> UserInDB:
        """Create a new user with the provided data."""
        new_user = User(**user_data.model_dump())
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return UserInDB.model_validate(new_user)

    async def get_by_id(self, user_id: int) -> UserInDB | None:
        """Retrieve a user by their ID and return as UserInDB schema."""
        user_obj = await self.session.get(User, user_id)
        if user_obj is None:
            return None
        return UserInDB.model_validate(user_obj)

    async def get_by_username(self, username: str) -> UserInDB | None:
        """Retrieve a user by their username."""
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        user_obj = result.scalar_one_or_none()
        if user_obj is None:
            return None
        return UserInDB.model_validate(user_obj)

    async def update(self, user_id: int, user_data: UserInDB) -> UserInDB | None:
        """Update an existing user's data."""
        user_obj = await self.session.get(User, user_id)
        if user_obj is None:
            return None
        for key, value in user_data.model_dump().items():
            setattr(user_obj, key, value)
        await self.session.commit()
        await self.session.refresh(user_obj)
        return UserInDB.model_validate(user_obj)

    async def delete(self, user_id: int) -> None:
        """Delete a user by their ID."""
        user_obj = await self.session.get(User, user_id)
        if user_obj:
            await self.session.delete(user_obj)
            await self.session.commit()

    async def soft_delete(self, user_id: int, actor_id: int) -> None:
        """Soft delete a user by their ID using AuditMixin helper."""
        user_obj = await self.session.get(User, user_id)
        if user_obj:
            user_obj.soft_delete(actor_id)
            await self.session.commit()
