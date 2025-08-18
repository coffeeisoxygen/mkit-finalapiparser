# pyright:reportArgumentType= false
# ruff:noqa
import pytest
from app.custom.exceptions.cst_exceptions import EntityAlreadyExistsError
from app.repositories.rep_member import AsyncInMemoryMemberRepo
from app.schemas.sch_member import MemberCreate, MemberDelete, MemberUpdate
from app.service.crud.member_service import MemberService
from hypothesis import given
from hypothesis import strategies as st

# Strategies for hypothesis
name_strategy = st.text(min_size=1, max_size=50)
pin_strategy = st.text(min_size=6, max_size=6)
password_strategy = st.text(min_size=8, max_size=20)
ipaddress_strategy = st.just("192.168.1.100")
report_url_strategy = st.just("http://localhost/report")
allow_nosign_strategy = st.just(False)


@pytest.mark.asyncio
@given(
    name=name_strategy,
    pin=pin_strategy,
    password=password_strategy,
    ipaddress=ipaddress_strategy,
    report_url=report_url_strategy,
    allow_nosign=allow_nosign_strategy,
)
async def test_create_member_success(
    name, pin, password, ipaddress, report_url, allow_nosign
):
    service = MemberService(AsyncInMemoryMemberRepo())
    data = MemberCreate(
        name=name,
        pin=pin,
        password=password,
        ipaddress=ipaddress,
        report_url=report_url,
        allow_nosign=allow_nosign,
    )
    member = await service.create(data)
    assert member.name == name


@pytest.mark.asyncio
async def test_create_member_duplicate_name():
    service = MemberService(AsyncInMemoryMemberRepo())
    data = MemberCreate(
        name="unique_name",
        pin="123456",
        password="password123",
        ipaddress="192.168.1.100",
        report_url="http://localhost/report",
        allow_nosign=False,
    )
    await service.create(data)
    with pytest.raises(EntityAlreadyExistsError):
        await service.create(data)


@pytest.mark.asyncio
async def test_update_member_name():
    service = MemberService(AsyncInMemoryMemberRepo())
    created = await service.create(
        MemberCreate(
            name="old_name",
            pin="123456",
            password="password123",
            ipaddress="192.168.1.100",
            report_url="http://localhost/report",
            allow_nosign=False,
        )
    )
    updated = await service.update(created.memberid, MemberUpdate(name="new_name"))
    assert updated.name == "new_name"


@pytest.mark.asyncio
async def test_delete_member():
    service = MemberService(AsyncInMemoryMemberRepo())
    created = await service.create(
        MemberCreate(
            name="to_delete",
            pin="123456",
            password="password123",
            ipaddress="192.168.1.100",
            report_url="http://localhost/report",
            allow_nosign=False,
        )
    )
    await service.remove(MemberDelete(memberid=created.memberid))
    with pytest.raises(Exception):
        await service.get(created.memberid)


@pytest.mark.asyncio
async def test_create_with_empty_name():
    service = MemberService(AsyncInMemoryMemberRepo())
    with pytest.raises(Exception):
        await service.create(
            MemberCreate(
                name="",
                pin="123456",
                password="password123",
                ipaddress="192.168.1.100",
                report_url="http://localhost/report",
                allow_nosign=False,
            )
        )


@pytest.mark.asyncio
async def test_create_with_short_pin():
    service = MemberService(AsyncInMemoryMemberRepo())
    with pytest.raises(Exception):
        await service.create(
            MemberCreate(
                name="Valid Name",
                pin="123",  # too short
                password="password123",
                ipaddress="192.168.1.100",
                report_url="http://localhost/report",
                allow_nosign=False,
            )
        )


@pytest.mark.asyncio
async def test_create_with_invalid_ip():
    service = MemberService(AsyncInMemoryMemberRepo())
    with pytest.raises(Exception):
        await service.create(
            MemberCreate(
                name="Valid Name",
                pin="123456",
                password="password123",
                ipaddress="999.999.999.999",  # invalid IP
                report_url="http://localhost/report",
                allow_nosign=False,
            )
        )


@pytest.mark.asyncio
async def test_create_with_invalid_url():
    service = MemberService(AsyncInMemoryMemberRepo())
    with pytest.raises(Exception):
        await service.create(
            MemberCreate(
                name="Valid Name",
                pin="123456",
                password="password123",
                ipaddress="192.168.1.100",
                report_url="not_a_url",  # invalid URL
                allow_nosign=False,
            )
        )


@pytest.mark.asyncio
async def test_update_member_with_empty_name():
    service = MemberService(AsyncInMemoryMemberRepo())
    created = await service.create(
        MemberCreate(
            name="Valid Name",
            pin="123456",
            password="password123",
            ipaddress="192.168.1.100",
            report_url="http://localhost/report",
            allow_nosign=False,
        )
    )
    with pytest.raises(Exception):
        await service.update(created.memberid, MemberUpdate(name=""))


@pytest.mark.asyncio
async def test_delete_nonexistent_member():
    service = MemberService(AsyncInMemoryMemberRepo())
    with pytest.raises(Exception):
        await service.remove(MemberDelete(memberid="NON_EXISTENT_ID"))
