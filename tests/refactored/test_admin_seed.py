"""Test for AdminSeedService (admin seeding and sysadmin protection)."""

import pytest
from app.models.db_user import User
from app.service.security.srv_hasher import HasherService
from app.service.user.srv_admin_seed import AdminSeedService
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_seed_default_admin_creates_admin(test_db_session: AsyncSession):
    service = AdminSeedService(test_db_session, hasher=HasherService())
    # Ensure no superuser exists
    await test_db_session.execute(delete(User))
    await test_db_session.commit()
    seeded = await service.seed_default_admin()
    assert seeded is True
    result = await test_db_session.execute(
        select(User).where(User.is_superuser.is_(True))
    )
    admin = result.scalar_one_or_none()
    assert admin is not None
    assert admin.username == "admin"


@pytest.mark.asyncio
async def test_seed_default_admin_skips_if_exists(test_db_session: AsyncSession):
    service = AdminSeedService(test_db_session, hasher=HasherService())
    await test_db_session.execute(delete(User))
    await test_db_session.commit()
    await service.seed_default_admin()
    seeded = await service.seed_default_admin()
    assert seeded is False
