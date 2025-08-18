import app.custom.exceptions as exc
import pytest
import pytest_asyncio
from app.repositories.rep_member import AsyncInMemoryMemberRepo
from app.schemas.sch_member import MemberCreate, MemberDelete, MemberUpdate
from app.service.srv_member import MemberService
from pydantic import ValidationError


@pytest.mark.asyncio
async def test_register_member_with_min_length_name(service):
    data = MemberCreate(
        name="A",  # min_length=1
        pin="123456",
        password="password123",
        ipaddress="192.168.1.10",
        report_url="http://localhost/reportmin",
        allow_nosign=False,
    )
    public = await service.create_member(data)
    assert public.name == "A"


@pytest.mark.asyncio
async def test_register_member_with_max_length_name(service):
    long_name = "A" * 100  # max_length=100
    data = MemberCreate(
        name=long_name,
        pin="123456",
        password="password123",
        ipaddress="192.168.1.11",
        report_url="http://localhost/reportmax",
        allow_nosign=False,
    )
    public = await service.create_member(data)
    assert public.name == long_name


@pytest.mark.asyncio
async def test_register_member_with_invalid_ip(service):
    with pytest.raises(ValidationError):
        data = MemberCreate(
            name="Invalid IP",
            pin="123456",
            password="password123",
            ipaddress="999.999.999.999",  # invalid IP
            report_url="http://localhost/reportip",
            allow_nosign=False,
        )
        await service.create_member(data)


@pytest.mark.asyncio
async def test_register_member_with_invalid_url(service):
    with pytest.raises(ValidationError):
        data = MemberCreate(
            name="Invalid URL",
            pin="123456",
            password="password123",
            ipaddress="192.168.1.12",
            report_url="not_a_url",  # invalid URL
            allow_nosign=False,
        )
        await service.create_member(data)


@pytest.mark.asyncio
async def test_register_member_with_short_pin(service):
    with pytest.raises(ValidationError):
        data = MemberCreate(
            name="Short Pin",
            pin="123",  # min_length=6
            password="password123",
            ipaddress="192.168.1.13",
            report_url="http://localhost/reportpin",
            allow_nosign=False,
        )
        await service.create_member(data)


@pytest.mark.asyncio
async def test_register_member_with_special_char_in_name(service):
    data = MemberCreate(
        name="Name!@#",  # allowed
        pin="123456",
        password="password123",
        ipaddress="192.168.1.14",
        report_url="http://localhost/reportspecial",
        allow_nosign=False,
    )
    public = await service.create_member(data)
    assert public.memberid.startswith("MEM")


# pyright: reportArgumentType= false


@pytest_asyncio.fixture
async def service():  # noqa: RUF029
    repo = AsyncInMemoryMemberRepo()
    return MemberService(repo)


@pytest.mark.asyncio
async def test_register_and_list_member(service: MemberService):
    data = MemberCreate(
        name="John Doe",
        pin="123456",
        password="password123",
        ipaddress="192.168.1.1",
        report_url="http://localhost/report",
        allow_nosign=False,
    )

    public = await service.create_member(data)
    assert public.name == "John Doe"
    assert public.memberid.startswith("MEM")

    members = await service.list_members()
    assert any(m.name == "John Doe" for m in members)


@pytest.mark.asyncio
async def test_update_member(service: MemberService):
    data = MemberCreate(
        name="Jane Doe",
        pin="654321",
        password="password456",
        ipaddress="192.168.1.2",
        report_url="http://localhost/report2",
        allow_nosign=True,
    )
    public = await service.create_member(data)
    update = MemberUpdate(name="Jane Updated")
    updated = await service.update_member(public.memberid, update)
    assert updated.name == "Jane Updated"


@pytest.mark.asyncio
async def test_remove_member(service: MemberService):
    data = MemberCreate(
        name="Remove Me",
        pin="111111",
        password="password789",
        ipaddress="192.168.1.3",
        report_url="http://localhost/report3",
        allow_nosign=False,
    )
    public = await service.create_member(data)
    await service.remove_member(MemberDelete(memberid=public.memberid))

    with pytest.raises(exc.EntityNotFoundError):
        await service.get_member(public.memberid)


@pytest.mark.asyncio
async def test_register_member_with_empty_fields(service: MemberService):
    with pytest.raises(ValidationError):
        data = MemberCreate(
            name="",
            pin="",
            password="",
            ipaddress="",
            report_url="",
            allow_nosign=False,
        )
        await service.create_member(data)
