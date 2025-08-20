"""this class is about default administrator seeding.

case:
    when theres no administrator user its will seed default admin user.
    then it will create a new user with is_superuser = true.
condition to meet:
    - jika tidak ada satupun record user dengan is_superuser = true
    - jika ada record user dengan is_superuser = true, maka tidak perlu melakukan seeding
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database.repositories.repo_user import SQLiteUserRepository
from app.mlogg import logger
from app.models.db_user import User
from app.schemas.sch_user import AdminSeeder, UserCreate
from app.service.security.srv_hasher import HasherService


class AdminSeedService:
    """Service to seed default admin and protect sysadmin accounts."""

    def __init__(self, session: AsyncSession, hasher: HasherService | None = None):
        self.session = session

        self.hasher = hasher or HasherService()
        self.log = logger.bind(service="AdminSeedService")

    async def has_active_superuser(self) -> bool:
        """Check if an active superuser exists.

        Returns True if exists, False otherwise.
        """
        stmt = select(User).where(
            User.is_superuser.is_(True),
            User.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        superuser = result.scalar_one_or_none()
        return bool(superuser and getattr(superuser, "is_active", True))

    async def seed_default_admin(
        self,
        admin_data: AdminSeeder | None = None,
        actor_id: uuid.UUID | None = None,
    ) -> bool:
        """Seed default admin if no active superuser exists.

        Returns True if seeded, False if already exists.
        """
        if await self.has_active_superuser():
            self.log.info("Active superuser already exists, skipping seeding.")
            return False
        # Use provided admin_data or default
        admin = admin_data or AdminSeeder(
            username="admin",
            email="admin@example.com",
            full_name="Default Admin",
            password="admin@123",
        )
        user_create = UserCreate(
            username=admin.username,
            email=admin.email,
            full_name=admin.full_name,
            password=admin.password,
        )
        # Hash password
        hashed_password = self.hasher.hash_value(user_create.password)

        # Use provided actor_id or default system UUID
        system_actor_id = actor_id or get_settings().ADM_ID
        repo = SQLiteUserRepository(self.session, autocommit=True)
        await repo.create(
            user_create,
            hashed_password,
            actor_id=system_actor_id,
            is_superuser=True,
        )
        self.log.info(
            "Default admin seeded.",
            username=admin.username,
            actor_id=str(system_actor_id),
        )
        return True
