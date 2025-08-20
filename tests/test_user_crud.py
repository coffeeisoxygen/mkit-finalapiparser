import uuid

import pytest
from app.config import get_settings
from app.custom.exceptions.cst_exceptions import (
    AdminCantDeleteError,
    DataDuplicationError,
    DataGenericError,
    DataNotFoundError,
)
from app.database.repositories.repo_user import ADM_ID
from app.models.db_user import User
from app.schemas.sch_user import UserCreate, UserUpdate
from app.service.user.srv_admin_seed import AdminSeedService
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
    with pytest.raises(DataNotFoundError):
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
    print(f"[DIAG] created.id={created.id} type={type(created.id)}")
    # Diagnostic: print user after creation
    result_pre = await test_db_session.execute(select(User))
    user_pre_list = result_pre.scalars().all()
    for user_pre in user_pre_list:
        print(
            f"[DIAG] DB user after creation: id={user_pre.id} type={type(user_pre.id)} username={user_pre.username} is_deleted_flag={user_pre.is_deleted_flag} deleted_at={user_pre.deleted_at}"
        )

    await service.soft_delete_user(created.id, actor_id=actor_id)
    # Diagnostic: print all users after soft delete
    all_result = await test_db_session.execute(select(User))
    all_users = all_result.scalars().all()
    print("[DIAG] All users after soft delete:")
    for u in all_users:
        print(
            f"id={u.id} type={type(u.id)} username={u.username} is_deleted_flag={u.is_deleted_flag} deleted_at={u.deleted_at}"
        )

    # Fetch directly from DB to check audit fields (no filter)
    result = await test_db_session.execute(
        select(User).where(User.id == str(created.id))
    )
    fetched = result.scalar_one_or_none()
    print(
        f"[DIAG] User after soft delete: id={fetched.id if fetched else None}, username={fetched.username if fetched else None}, is_deleted_flag={fetched.is_deleted_flag if fetched else None}, deleted_at={fetched.deleted_at if fetched else None}"
    )
    assert fetched is not None, "User should exist after soft delete"
    assert fetched.deleted_at is not None
    assert str(fetched.deleted_by) == str(actor_id)


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
    with pytest.raises(DataDuplicationError):
        await service.create_user(user2, actor_id=actor_id)


@pytest.mark.asyncio
async def test_get_user_by_invalid_id(test_db_session):
    service = UserCrudService(test_db_session)
    invalid_id = uuid.uuid4()
    with pytest.raises(DataNotFoundError):
        await service.get_user_by_id(invalid_id)


@pytest.mark.asyncio
async def test_update_nonexistent_user(test_db_session):
    service = UserCrudService(test_db_session)
    invalid_id = uuid.uuid4()
    update = UserUpdate(full_name="Should Not Exist")
    actor_id = uuid.uuid4()
    with pytest.raises(DataNotFoundError):
        await service.update_user(invalid_id, update, actor_id=actor_id)


@pytest.mark.asyncio
async def test_delete_nonexistent_user(test_db_session):
    service = UserCrudService(test_db_session)
    invalid_id = uuid.uuid4()
    with pytest.raises(DataNotFoundError):
        await service.delete_user(invalid_id)


@pytest.mark.asyncio
async def test_soft_delete_nonexistent_user(test_db_session):
    service = UserCrudService(test_db_session)
    invalid_id = uuid.uuid4()
    actor_id = uuid.uuid4()
    with pytest.raises(DataGenericError):
        await service.soft_delete_user(invalid_id, actor_id=actor_id)


def test_create_user_empty_fields():
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
    # Ensure admin exists using seeder
    await AdminSeedService(test_db_session).seed_default_admin()
    # Diagnostic: fetch admin user directly after seeding
    admin_result = await test_db_session.execute(select(User).where(User.id == adm_id))
    admin_user = admin_result.scalar_one_or_none()
    print(
        f"[DIAG] Admin user after seeding: id={admin_user.id if admin_user else None}, username={admin_user.username if admin_user else None}, is_deleted_flag={admin_user.is_deleted_flag if admin_user else None}, deleted_at={admin_user.deleted_at if admin_user else None}"
    )
    # Try to delete admin
    with pytest.raises(AdminCantDeleteError):
        await service.delete_user(adm_id)
    with pytest.raises(AdminCantDeleteError):
        await service.delete_user(ADM_ID)
        await service.delete_user(adm_id)
    with pytest.raises(AdminCantDeleteError):
        await service.delete_user(ADM_ID)
