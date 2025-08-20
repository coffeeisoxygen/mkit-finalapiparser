import uuid

import pytest
from app.custom.exceptions.cst_exceptions import (
    AdminCantDeleteError,
    DataDuplicationError,
    DataNotFoundError,
)
from app.database.repositories.repo_user import ADM_ID, SQLiteUserRepository
from app.models.db_user import User
from app.schemas.sch_user import UserCreate, UserUpdate
from sqlalchemy import select


@pytest.mark.asyncio
async def test_repo_user_crud(test_db_session):
    repo = SQLiteUserRepository(test_db_session)
    actor_id = uuid.uuid4()
    user = UserCreate(
        username="repo_user",
        email="repo_user@example.com",
        full_name="Repo User",
        password="password@123",
    )
    # Create
    created = await repo.create(user, hashed_password="hashed", actor_id=actor_id)
    assert created.username == user.username
    assert created.email == user.email
    # Get by ID (always str)
    fetched = await repo.get_by_id(str(created.id))
    assert fetched.id == created.id
    # Update
    update = UserUpdate(full_name="Repo User Updated")
    updated = await repo.update(str(created.id), update, actor_id=actor_id)
    assert updated.full_name == "Repo User Updated"
    # Duplicate
    with pytest.raises(DataDuplicationError):
        await repo.create(user, hashed_password="hashed", actor_id=actor_id)
    # Delete
    await repo.delete(str(created.id))
    with pytest.raises(DataNotFoundError):
        await repo.get_by_id(str(created.id))


@pytest.mark.asyncio
async def test_repo_user_soft_delete(test_db_session):
    repo = SQLiteUserRepository(test_db_session)
    actor_id = uuid.uuid4()
    user = UserCreate(
        username="repo_softdel",
        email="repo_softdel@example.com",
        full_name="Repo SoftDel",
        password="password@123",
    )
    created = await repo.create(user, hashed_password="hashed", actor_id=actor_id)
    await repo.soft_delete(str(created.id), str(actor_id))
    # Direct DB query
    result = await test_db_session.execute(
        select(User).where(User.id == str(created.id))
    )
    fetched = result.scalar_one_or_none()
    assert fetched.is_deleted_flag is True
    assert str(fetched.deleted_by) == str(actor_id)
    assert fetched.deleted_at is not None


@pytest.mark.asyncio
async def test_repo_user_admin_cannot_delete(test_db_session):
    from app.service.user.srv_admin_seed import AdminSeedService

    # Ensure admin exists using seeder
    await AdminSeedService(test_db_session).seed_default_admin()
    repo = SQLiteUserRepository(test_db_session)
    with pytest.raises(AdminCantDeleteError):
        await repo.delete(str(ADM_ID))
