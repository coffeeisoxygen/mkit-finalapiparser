import pytest
from app.custom.cst_exceptions import EntityNotFoundError
from app.repositories.rep_module import InMemoryModuleRepository
from app.schemas.sch_module import ModuleCreate, ModuleDelete, ModuleUpdate
from app.service.srv_module import ModuleService
from hypothesis import given
from hypothesis import strategies as st
from pydantic import SecretStr

# Strategies for fields
provider_st = st.sampled_from(["DIGIPOS", "ISIMPLE"])  # Adjust as needed
name_st = st.text(min_size=1, max_size=20)
base_url_st = st.just("http://localhost:8000")  # Any valid URL
allowed_username_chars = (
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
)
username_st = st.text(min_size=1, max_size=12, alphabet=allowed_username_chars)
msisdn_st = st.from_regex(r"^\+?[1-9]\d{1,14}$", fullmatch=True)
pin_st = st.text(
    min_size=4, max_size=8, alphabet=st.characters(whitelist_categories=["Nd"])
)
password_st = st.text(min_size=4, max_size=16)
email_st = st.just("user@example.com")


@given(
    provider=provider_st,
    name=name_st,
    base_url=base_url_st,
    username=username_st,
    msisdn=msisdn_st,
    pin=pin_st,
    password=password_st,
    email=email_st,
)
def test_create_module_hypothesis(
    provider, name, base_url, username, msisdn, pin, password, email
):
    repo = InMemoryModuleRepository()
    service = ModuleService(repo)
    data = ModuleCreate(
        provider=provider,
        name=name,
        base_url=base_url,
        username=SecretStr(username),
        msisdn=SecretStr(msisdn),
        pin=SecretStr(pin),
        password=SecretStr(password),
        email=email,
    )
    result = service.create_module(data)
    assert result.moduleid.startswith("MOD")
    assert isinstance(result.moduleid, str)


@given(
    provider=provider_st,
    name=name_st,
    base_url=base_url_st,
    username=username_st,
    msisdn=msisdn_st,
    pin=pin_st,
    password=password_st,
    email=email_st,
)
def test_update_module_hypothesis(
    provider, name, base_url, username, msisdn, pin, password, email
):
    repo = InMemoryModuleRepository()
    service = ModuleService(repo)
    data = ModuleCreate(
        provider=provider,
        name=name,
        base_url=base_url,
        username=SecretStr(username),
        msisdn=SecretStr(msisdn),
        pin=SecretStr(pin),
        password=SecretStr(password),
        email=email,
    )
    created = service.create_module(data)
    update_data = ModuleUpdate(
        moduleid=created.moduleid,
        name="UpdatedName",
        is_active=False,
    )
    updated = service.update_module(created.moduleid, update_data)
    assert updated.moduleid == created.moduleid
    assert updated.moduleid.startswith("MOD")


@given(
    provider=provider_st,
    name=name_st,
    base_url=base_url_st,
    username=username_st,
    msisdn=msisdn_st,
    pin=pin_st,
    password=password_st,
    email=email_st,
)
def test_remove_module_hypothesis(
    provider, name, base_url, username, msisdn, pin, password, email
):
    repo = InMemoryModuleRepository()
    service = ModuleService(repo)
    data = ModuleCreate(
        provider=provider,
        name=name,
        base_url=base_url,
        username=SecretStr(username),
        msisdn=SecretStr(msisdn),
        pin=SecretStr(pin),
        password=SecretStr(password),
        email=email,
    )
    created = service.create_module(data)
    delete_data = ModuleDelete(moduleid=created.moduleid)
    service.remove_module(delete_data)
    with pytest.raises(EntityNotFoundError):
        service.get_module(created.moduleid)
