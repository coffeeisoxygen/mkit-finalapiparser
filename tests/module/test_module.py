# pyright: reportArgumentType=false
# ruff : noqa
import app.custom.exceptions as exc
import pytest
from app.config import ProviderEnums
from app.repositories.rep_module import InMemoryModuleRepository
from app.schemas.sch_module import ModuleCreate, ModuleDelete, ModuleUpdate
from app.service.srv_module import ModuleService
from pydantic import SecretStr, ValidationError


def test_register_module_with_min_length_name(service):
    data = ModuleCreate(
        provider=ProviderEnums.DIGIPOS,
        name="A",  # min_length=1
        username=str("user1"),
        msisdn=str("628123456789"),
        pin=str("123456"),
        password=str("password123"),
        email="test@example.com",
        base_url="http://localhost/min",
    )
    public = service.create_module(data)
    assert public.moduleid.startswith("MOD")


def test_register_module_with_max_length_name(service):
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
    public = service.create_module(data)
    assert public.moduleid.startswith("MOD")


def test_register_module_with_invalid_ip(service):
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


def test_register_module_with_invalid_url(service):
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


def test_register_module_with_short_pin(service):
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


def test_register_module_with_special_char_in_name(service):
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
    public = service.create_module(data)
    assert public.moduleid.startswith("MOD")


@pytest.fixture
def service():
    repo = InMemoryModuleRepository()
    return ModuleService(repo)


def test_register_and_list_module(service: ModuleService):
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
    public = service.create_module(data)
    assert public.moduleid.startswith("MOD")
    modules = service.list_modules()
    assert any(m.moduleid == public.moduleid for m in modules)


def test_update_module(service: ModuleService):
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
    public = service.create_module(data)
    update = ModuleUpdate(name="Module Updated")
    updated = service.update_module(public.moduleid, update)
    assert updated.moduleid == public.moduleid


def test_remove_module(service: ModuleService):
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
    public = service.create_module(data)
    service.remove_module(ModuleDelete(moduleid=public.moduleid))

    with pytest.raises(exc.EntityNotFoundError):
        service.update_module(public.moduleid, ModuleUpdate(name="Should Fail"))


def test_register_module_with_empty_fields(service: ModuleService):
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
