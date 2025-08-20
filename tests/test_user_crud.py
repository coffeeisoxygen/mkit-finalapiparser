import contextlib
import uuid

import pytest
from app.config import get_settings
from app.custom.exceptions.cst_exceptions import AdminCantDeleteError
from app.database.repositories.repo_user import ADM_ID
from app.models.db_user import User
from app.schemas.sch_user import UserCreate, UserUpdate
from app.service.user.srv_user_crud import UserCrudService
from pydantic import ValidationError
from sqlalchemy import select


@pytest.mark.asyncio
async def test_create_user(test_db_session):
    service = UserCrudService(test_db_session)
    user = UserCreate(
        username="testuser",
        email="testuser@example.com",
        full_name="Test User",
        password="password@123",
    )
    actor_id = uuid.uuid4()
    created = await service.create_user(user, actor_id=actor_id)
    assert created.username == user.username
    assert created.email == user.email
    assert created.full_name == user.full_name
    assert created.id is not None


@pytest.mark.asyncio
async def test_get_user_by_id(test_db_session):
    service = UserCrudService(test_db_session)
    user = UserCreate(
        username="getbyid",
        email="getbyid@example.com",
        full_name="Get By Id",
        password="password@123",
    )
    actor_id = uuid.uuid4()
    created = await service.create_user(user, actor_id=actor_id)
    fetched = await service.get_user_by_id(created.id)
    assert fetched.username == user.username
    assert fetched.email == user.email


@pytest.mark.asyncio
async def test_get_user_by_username(test_db_session):
    service = UserCrudService(test_db_session)
    user = UserCreate(
        username="getbyusername",
        email="getbyusername@example.com",
        full_name="Get By Username",
        password="password@123",
    )
    actor_id = uuid.uuid4()
    created = await service.create_user(user, actor_id=actor_id)
    fetched = await service.get_user_by_username(user.username)
    assert fetched.id == created.id


@pytest.mark.asyncio
async def test_list_users(test_db_session):
    service = UserCrudService(test_db_session)
    users = await service.list_users()
    assert isinstance(users, list)


@pytest.mark.asyncio
async def test_update_user(test_db_session):
    service = UserCrudService(test_db_session)
    user = UserCreate(
        username="updateuser",
        email="updateuser@example.com",
        full_name="Update User",
        password="password@123",
    )
    actor_id = uuid.uuid4()
    created = await service.create_user(user, actor_id=actor_id)
    update = UserUpdate(full_name="Updated Name")
    updated = await service.update_user(created.id, update, actor_id=actor_id)
    assert updated.full_name == "Updated Name"


@pytest.mark.asyncio
async def test_delete_user(test_db_session):
    service = UserCrudService(test_db_session)
    user = UserCreate(
        username="deleteuser",
        email="deleteuser@example.com",
        full_name="Delete User",
        password="password@123",
    )
    actor_id = uuid.uuid4()
    created = await service.create_user(user, actor_id=actor_id)
    await service.delete_user(created.id)
    with pytest.raises(Exception):  # noqa: B017
        await service.get_user_by_id(created.id)


@pytest.mark.asyncio
async def test_soft_delete_user(test_db_session):
    service = UserCrudService(test_db_session)
    user = UserCreate(
        username="softdeleteuser",
        email="softdeleteuser@example.com",
        full_name="Soft Delete User",
        password="password@123",
    )
    actor_id = uuid.uuid4()
    created = await service.create_user(user, actor_id=actor_id)
    await service.soft_delete_user(created.id, actor_id=actor_id)
    # Fetch directly from DB to check audit fields

    result = await test_db_session.execute(select(User).where(User.id == created.id))
    fetched = result.scalar_one()
    assert fetched.deleted_at is not None
    assert fetched.deleted_by == actor_id


@pytest.mark.asyncio
async def test_create_user_duplicate_username_email(test_db_session):
    service = UserCrudService(test_db_session)
    user1 = UserCreate(
        username="edgeuser",
        email="edgeuser@example.com",
        full_name="Edge User",
        password="password@123",
    )
    actor_id = uuid.uuid4()
    await service.create_user(user1, actor_id=actor_id)
    user2 = UserCreate(
        username="edgeuser",
        email="edgeuser@example.com",
        full_name="Edge User 2",
        password="password@456",
    )
    with pytest.raises(Exception):
        await service.create_user(user2, actor_id=actor_id)


@pytest.mark.asyncio
async def test_get_user_by_invalid_id(test_db_session):
    service = UserCrudService(test_db_session)
    invalid_id = uuid.uuid4()
    with pytest.raises(Exception):
        await service.get_user_by_id(invalid_id)


@pytest.mark.asyncio
async def test_update_nonexistent_user(test_db_session):
    service = UserCrudService(test_db_session)
    invalid_id = uuid.uuid4()
    update = UserUpdate(full_name="Should Not Exist")
    actor_id = uuid.uuid4()
    with pytest.raises(Exception):
        await service.update_user(invalid_id, update, actor_id=actor_id)


@pytest.mark.asyncio
async def test_delete_nonexistent_user(test_db_session):
    service = UserCrudService(test_db_session)
    invalid_id = uuid.uuid4()
    with pytest.raises(Exception):
        await service.delete_user(invalid_id)


@pytest.mark.asyncio
async def test_soft_delete_nonexistent_user(test_db_session):
    service = UserCrudService(test_db_session)
    invalid_id = uuid.uuid4()
    actor_id = uuid.uuid4()
    with pytest.raises(Exception):
        await service.soft_delete_user(invalid_id, actor_id=actor_id)


@pytest.mark.asyncio
async def test_create_user_empty_fields(test_db_session):
    service = UserCrudService(test_db_session)
    actor_id = uuid.uuid4()
    with pytest.raises(ValidationError):
        UserCreate(
            username="",
            email="",
            full_name="",
            password="",
        )


@pytest.mark.asyncio
async def test_admin_cannot_be_deleted(test_db_session):
    settings = get_settings()
    adm_id = uuid.UUID(str(settings.ADM_ID))
    service = UserCrudService(test_db_session)
    # Ensure admin exists
    user = UserCreate(
        username="admin",
        email="admin@example.com",
        full_name="Default Admin",
        password="admin@123",
    )
    actor_id = uuid.uuid4()
    with contextlib.suppress(Exception):
        await service.create_user(user, actor_id=actor_id)
    # Try to delete admin
    with pytest.raises(AdminCantDeleteError):
        await service.delete_user(adm_id)
    # Try to delete admin
    with pytest.raises(AdminCantDeleteError):
        await service.delete_user(ADM_ID)
