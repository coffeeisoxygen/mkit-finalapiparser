# pyright:reportArgumentType= false
# ruff:noqa
import pytest
from app.repositories.rep_module import AsyncInMemoryModuleRepo
from app.schemas.sch_module import (
    ModuleCreate,
    ModuleDelete,
    ModuleUpdate,
    ProviderEnums,
)
from app.service.crud.module_service import ModuleService
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

# Strategies for fields
name_strategy = st.text(min_size=1, max_size=50)
provider_strategy = st.sampled_from([ProviderEnums.DIGIPOS, ProviderEnums.ISIMPLE])
username_strategy = st.text(min_size=1, max_size=30)
msisdn_strategy = st.text(min_size=10, max_size=15)
pin_strategy = st.text(min_size=6, max_size=6)
password_strategy = st.text(min_size=8, max_size=20)
email_strategy = st.just("test@example.com")
base_url_strategy = st.just("http://localhost/api")


@pytest.mark.asyncio
def service():
    return ModuleService(AsyncInMemoryModuleRepo())


@given(
    name=name_strategy,
    provider=provider_strategy,
    username=username_strategy,
    msisdn=msisdn_strategy,
    pin=pin_strategy,
    password=password_strategy,
    email=email_strategy,
    base_url=base_url_strategy,
)
@pytest.mark.asyncio
async def test_create_and_get_module(
    name, provider, username, msisdn, pin, password, email, base_url
):
    svc = ModuleService(AsyncInMemoryModuleRepo())
    data = ModuleCreate(
        name=name,
        provider=provider,
        username=username,
        msisdn=msisdn,
        pin=pin,
        password=password,
        email=email,
        base_url=base_url,
    )
    created = await svc.create(data)
    assert created.name == name
    fetched = await svc.get(created.moduleid)
    assert fetched == created


@given(
    name=name_strategy,
    provider=provider_strategy,
    username=username_strategy,
    msisdn=msisdn_strategy,
    pin=pin_strategy,
    password=password_strategy,
    email=email_strategy,
    base_url=base_url_strategy,
)
@pytest.mark.asyncio
async def test_update_module(
    name, provider, username, msisdn, pin, password, email, base_url
):
    svc = ModuleService(AsyncInMemoryModuleRepo())
    created = await svc.create(
        ModuleCreate(
            name="dummy",
            provider=provider,
            username=username,
            msisdn=msisdn,
            pin=pin,
            password=password,
            email=email,
            base_url=base_url,
        )
    )
    updated = await svc.update(created.moduleid, ModuleUpdate(name=name))
    assert updated.name == name


@given(
    name=name_strategy,
    provider=provider_strategy,
    username=username_strategy,
    msisdn=msisdn_strategy,
    pin=pin_strategy,
    password=password_strategy,
    email=email_strategy,
    base_url=base_url_strategy,
)
@pytest.mark.asyncio
async def test_delete_module(
    name, provider, username, msisdn, pin, password, email, base_url
):
    svc = ModuleService(AsyncInMemoryModuleRepo())
    created = await svc.create(
        ModuleCreate(
            name=name,
            provider=provider,
            username=username,
            msisdn=msisdn,
            pin=pin,
            password=password,
            email=email,
            base_url=base_url,
        )
    )
    await svc.remove(ModuleDelete(moduleid=created.moduleid))
    with pytest.raises(Exception):
        await svc.get(created.moduleid)


@pytest.mark.asyncio
async def test_create_with_empty_name():
    svc = ModuleService(AsyncInMemoryModuleRepo())
    with pytest.raises(ValidationError):
        await svc.create(
            ModuleCreate(
                name="",
                provider=ProviderEnums.DIGIPOS,
                username="user",
                msisdn="081234567890",
                pin="123456",
                password="password123",
                email="test@example.com",
                base_url="http://localhost/api",
            )
        )


@pytest.mark.asyncio
async def test_create_with_short_pin():
    svc = ModuleService(AsyncInMemoryModuleRepo())
    with pytest.raises(ValidationError):
        await svc.create(
            ModuleCreate(
                name="Valid Name",
                provider=ProviderEnums.DIGIPOS,
                username="user",
                msisdn="081234567890",
                pin="123",
                password="password123",
                email="test@example.com",
                base_url="http://localhost/api",
            )
        )


@pytest.mark.asyncio
async def test_create_with_invalid_email():
    svc = ModuleService(AsyncInMemoryModuleRepo())
    with pytest.raises(ValidationError):
        await svc.create(
            ModuleCreate(
                name="Valid Name",
                provider=ProviderEnums.DIGIPOS,
                username="user",
                msisdn="081234567890",
                pin="123456",
                password="password123",
                email="not-an-email",
                base_url="http://localhost/api",
            )
        )


@pytest.mark.asyncio
async def test_create_with_invalid_url():
    svc = ModuleService(AsyncInMemoryModuleRepo())
    with pytest.raises(ValidationError):
        await svc.create(
            ModuleCreate(
                name="Valid Name",
                provider=ProviderEnums.DIGIPOS,
                username="user",
                msisdn="081234567890",
                pin="123456",
                password="password123",
                email="test@example.com",
                base_url="not_a_url",
            )
        )


@pytest.mark.asyncio
async def test_update_module_with_empty_name():
    svc = ModuleService(AsyncInMemoryModuleRepo())
    created = await svc.create(
        ModuleCreate(
            name="Valid Name",
            provider=ProviderEnums.DIGIPOS,
            username="user",
            msisdn="081234567890",
            pin="123456",
            password="password123",
            email="test@example.com",
            base_url="http://localhost/api",
        )
    )
    with pytest.raises(ValidationError):
        await svc.update(created.moduleid, ModuleUpdate(name=""))


@pytest.mark.asyncio
async def test_delete_nonexistent_module():
    svc = ModuleService(AsyncInMemoryModuleRepo())
    with pytest.raises(Exception):
        await svc.remove(ModuleDelete(moduleid="NON_EXISTENT_ID"))
