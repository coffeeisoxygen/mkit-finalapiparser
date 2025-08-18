# pyright: reportArgumentType=false
# ruff : noqa
import app.custom.exceptions as exc
import pytest
from app.schemas.sch_module import ProviderEnums
from app.repositories.rep_module import AsyncInMemoryModuleRepo
from app.schemas.sch_module import ModuleCreate, ModuleDelete, ModuleUpdate
from app.service import ModuleService
from pydantic import SecretStr, ValidationError


import pytest_asyncio


@pytest.mark.asyncio
async def test_register_module_with_min_length_name(service):
    data = ModuleCreate(
        provider=ProviderEnums.DIGIPOS,
        name="A",  # min_length=1
        username="user1",
        msisdn="628123456789",
        pin="123456",
        password="password123",
        email="test@example.com",
        base_url="http://localhost/min",
    )
    public = await service.create(data)
    assert public.moduleid.startswith("MOD")


@pytest.mark.asyncio
async def test_register_module_with_max_length_name(service):
    long_name = "A" * 100  # max_length=100
    data = ModuleCreate(
        provider=ProviderEnums.DIGIPOS,
        name=long_name,
        username="user2",
        msisdn="628123456789",
        pin="123456",
        password="password123",
        email="test@example.com",
        base_url="http://localhost/max",
    )
    public = await service.create(data)
    assert public.moduleid.startswith("MOD")


@pytest.mark.asyncio
async def test_register_module_with_invalid_ip(service):
    with pytest.raises(ValidationError):
        ModuleCreate(
            provider=ProviderEnums.DIGIPOS,
            name="Invalid IP",
            username="user3",
            msisdn="628123456789",
            pin="123456",
            password="password123",
            email="test@example.com",
            base_url="http://999.999.999.999",
        )


@pytest.mark.asyncio
async def test_register_module_with_invalid_url(service):
    with pytest.raises(ValidationError):
        ModuleCreate(
            provider=ProviderEnums.DIGIPOS,
            name="Invalid URL",
            username="user4",
            msisdn="628123456789",
            pin="123456",
            password="password123",
            email="test@example.com",
            base_url="not_a_url",
        )


@pytest.mark.asyncio
async def test_register_module_with_short_pin(service):
    with pytest.raises(ValidationError):
        ModuleCreate(
            provider=ProviderEnums.DIGIPOS,
            name="Short Pin",
            username="user5",
            msisdn="628123456789",
            pin="123",  # min_length=6
            password="password123",
            email="test@example.com",
            base_url="http://localhost/pin",
        )


@pytest.mark.asyncio
async def test_register_module_with_special_char_in_name(service):
    data = ModuleCreate(
        provider=ProviderEnums.DIGIPOS,
        name="Name!@#",  # allowed
        username="user6",
        msisdn="628123456789",
        pin="123456",
        password="password123",
        email="test@example.com",
        base_url="http://localhost/special",
    )
    public = await service.create(data)
    assert public.moduleid.startswith("MOD")


@pytest_asyncio.fixture
async def service():
    repo = AsyncInMemoryModuleRepo()
    return ModuleService(repo)


@pytest.mark.asyncio
async def test_register_and_list_module(service):
    data = ModuleCreate(
        provider=ProviderEnums.DIGIPOS,
        name="Module One",
        username="user7",
        msisdn="628123456789",
        pin="123456",
        password="password123",
        email="test@example.com",
        base_url="http://localhost/one",
    )
    public = await service.create(data)
    assert public.moduleid.startswith("MOD")
    modules = await service.list()
    assert any(m.moduleid == public.moduleid for m in modules)


@pytest.mark.asyncio
async def test_update_module(service):
    data = ModuleCreate(
        provider=ProviderEnums.DIGIPOS,
        name="Module Two",
        username="user8",
        msisdn="628123456789",
        pin="654321",
        password="password456",
        email="test@example.com",
        base_url="http://localhost/two",
    )
    public = await service.create(data)
    update = ModuleUpdate(name="Module Updated")
    updated = await service.update(public.moduleid, update)
    assert updated.moduleid == public.moduleid


@pytest.mark.asyncio
async def test_remove_module(service):
    data = ModuleCreate(
        provider=ProviderEnums.DIGIPOS,
        name="Remove Me",
        username="user9",
        msisdn="628123456789",
        pin="111111",
        password="password789",
        email="test@example.com",
        base_url="http://localhost/remove",
    )
    public = await service.create(data)
    await service.remove(ModuleDelete(moduleid=public.moduleid))

    with pytest.raises(exc.EntityNotFoundError):
        await service.update(public.moduleid, ModuleUpdate(name="Should Fail"))


@pytest.mark.asyncio
async def test_register_module_with_empty_fields(service):
    with pytest.raises(ValidationError):
        ModuleCreate(
            provider=ProviderEnums.DIGIPOS,
            name="",
            username="",
            msisdn="",
            pin="",
            password="",
            email="",
            base_url="",
        )
