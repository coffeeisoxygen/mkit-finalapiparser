import pytest
from app.schemas.sch_user import UserCreate, UserUpdate
from app.service.user.srv_user_crud import UserCrudService


@pytest.mark.asyncio
async def test_create_user(test_db_session):
    service = UserCrudService(test_db_session)
    user = UserCreate(
        username="testuser",
        email="testuser@example.com",
        full_name="Test User",
        password="password123",
    )
    created = await service.create_user(user, actor_id=1)
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
        password="password123",
    )
    created = await service.create_user(user, actor_id=2)
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
        password="password123",
    )
    created = await service.create_user(user, actor_id=3)
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
        password="password123",
    )
    created = await service.create_user(user, actor_id=4)
    update = UserUpdate(full_name="Updated Name")
    updated = await service.update_user(created.id, update, actor_id=4)
    assert updated.full_name == "Updated Name"


@pytest.mark.asyncio
async def test_delete_user(test_db_session):
    service = UserCrudService(test_db_session)
    user = UserCreate(
        username="deleteuser",
        email="deleteuser@example.com",
        full_name="Delete User",
        password="password123",
    )
    created = await service.create_user(user, actor_id=5)
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
        password="password123",
    )
    created = await service.create_user(user, actor_id=6)
    await service.soft_delete_user(created.id, actor_id=6)
    fetched = await service.get_user_by_id(created.id)
    assert fetched.deleted_at is not None
    assert fetched.deleted_by == 6
