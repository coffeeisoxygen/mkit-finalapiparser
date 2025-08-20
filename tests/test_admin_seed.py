"""Test for AdminSeedService (admin seeding and sysadmin protection)."""

import uuid

import pytest
from app.models.db_user import User
from app.service.security.srv_hasher import HasherService
from app.service.user.srv_admin_seed import AdminSeedService
from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_seed_default_admin_creates_admin(test_db_session: AsyncSession):
    service = AdminSeedService(test_db_session, hasher=HasherService())
    # Ensure no superuser exists
    await test_db_session.execute(delete(User))
    await test_db_session.commit()
    system_actor_id = uuid.UUID("00000000-0000-0000-0000-000000000000")
    seeded = await service.seed_default_admin(actor_id=system_actor_id)
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
    system_actor_id = uuid.UUID("00000000-0000-0000-0000-000000000000")
    await service.seed_default_admin(actor_id=system_actor_id)
    seeded = await service.seed_default_admin(actor_id=system_actor_id)
    assert seeded is False


@pytest.mark.asyncio
async def test_can_delete_user_false_for_superuser(test_db_session: AsyncSession):
    service = AdminSeedService(test_db_session, hasher=HasherService())
    await test_db_session.execute(delete(User))
    await test_db_session.commit()
    system_actor_id = uuid.UUID("00000000-0000-0000-0000-000000000000")
    await service.seed_default_admin(actor_id=system_actor_id)
    result = await test_db_session.execute(
        select(User.id).where(User.is_superuser.is_(True))
    )
    admin_id = result.scalar_one()
    can_delete = await service.can_delete_user(admin_id)
    assert can_delete is False


@pytest.mark.asyncio
async def test_can_delete_user_true_for_normal_user(test_db_session: AsyncSession):
    service = AdminSeedService(test_db_session, hasher=HasherService())
    await test_db_session.execute(delete(User))
    await test_db_session.commit()
    # Create normal user
    stmt = insert(User).values(
        username="user1",
        email="user1@example.com",
        full_name="User One",
        hashed_password="hashed",
        is_superuser=False,
    )
    await test_db_session.execute(stmt)
    await test_db_session.commit()
    result = await test_db_session.execute(
        select(User.id).where(User.is_superuser.is_(False))
    )
    user_id = result.scalar_one()
    can_delete = await service.can_delete_user(user_id)
    assert can_delete is True
