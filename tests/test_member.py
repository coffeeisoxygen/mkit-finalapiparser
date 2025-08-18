import app.custom.exceptions as exc
import pytest
import pytest_asyncio
from app.repositories.rep_member import AsyncInMemoryMemberRepo
from app.schemas.sch_member import MemberCreate, MemberDelete, MemberUpdate
from app.service import MemberService
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
    public = await service.create(data)
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
    public = await service.create(data)
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
        await service.create(data)


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
        await service.create(data)


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
        await service.create(data)


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
    public = await service.create(data)
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

    public = await service.create(data)
    assert public.name == "John Doe"
    assert public.memberid.startswith("MEM")

    members = await service.list()
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
    public = await service.create(data)
    update = MemberUpdate(name="Jane Updated")
    updated = await service.update(public.memberid, update)
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
    public = await service.create(data)
    await service.remove(MemberDelete(memberid=public.memberid))

    with pytest.raises(exc.EntityNotFoundError):
        await service.get(public.memberid)


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
        await service.create(data)


@pytest.mark.asyncio
async def test_memberid_auto_generation(service: MemberService):
    data = MemberCreate(
        name="AutoGen Member",
        pin="123456",
        password="password123",
        ipaddress="192.168.1.15",
        report_url="http://localhost/reportautogen",
        allow_nosign=False,
    )
    public = await service.create(data)
    assert public.memberid.startswith("MEM")


@pytest.mark.asyncio
async def test_register_member_with_duplicate_pin(service: MemberService):
    data1 = MemberCreate(
        name="Member One",
        pin="123456",
        password="password123",
        ipaddress="192.168.1.16",
        report_url="http://localhost/reportdup1",
        allow_nosign=False,
    )
    data2 = MemberCreate(
        name="Member Two",
        pin="123456",  # duplicate pin
        password="password456",
        ipaddress="192.168.1.17",
        report_url="http://localhost/reportdup2",
        allow_nosign=False,
    )
    await service.create(data1)
    with pytest.raises(ValidationError):
        await service.create(data2)


@pytest.mark.asyncio
async def test_register_member_with_duplicate_name(service: MemberService):
    data1 = MemberCreate(
        name="Duplicate Name",
        pin="123456",
        password="password123",
        ipaddress="192.168.1.18",
        report_url="http://localhost/reportdupname1",
        allow_nosign=False,
    )
    data2 = MemberCreate(
        name="Duplicate Name",  # duplicate name
        pin="654321",
        password="password456",
        ipaddress="192.168.1.19",
        report_url="http://localhost/reportdupname2",
        allow_nosign=False,
    )
    await service.create(data1)
    with pytest.raises(ValidationError):
        await service.create(data2)


@pytest.mark.asyncio
async def test_update_member_ipaddress(service: MemberService):
    data = MemberCreate(
        name="Ip Update Member",
        pin="123456",
        password="password123",
        ipaddress="192.168.1.20",
        report_url="http://localhost/reportipupdate",
        allow_nosign=False,
    )
    public = await service.create(data)
    update = MemberUpdate(ipaddress="192.168.1.21")
    updated = await service.update(public.memberid, update)
    assert updated.ipaddress == "192.168.1.21"


@pytest.mark.asyncio
async def test_update_member_report_url(service: MemberService):
    data = MemberCreate(
        name="URL Update Member",
        pin="123456",
        password="password123",
        ipaddress="192.168.1.22",
        report_url="http://localhost/reporturlupdate",
        allow_nosign=False,
    )
    public = await service.create(data)
    update = MemberUpdate(report_url="http://localhost/newreporturl")
    updated = await service.update(public.memberid, update)
    assert updated.report_url == "http://localhost/newreporturl"


@pytest.mark.asyncio
async def test_member_creation_without_allow_nosign(service: MemberService):
    data = MemberCreate(
        name="No Sign Member",
        pin="123456",
        password="password123",
        ipaddress="192.168.1.23",
        report_url="http://localhost/reportnosign",
        allow_nosign=False,
    )
    public = await service.create(data)
    assert public.allow_nosign is False


@pytest.mark.asyncio
async def test_member_creation_with_allow_nosign(service: MemberService):
    data = MemberCreate(
        name="Sign Member",
        pin="123456",
        password="password123",
        ipaddress="192.168.1.24",
        report_url="http://localhost/reportallow",
        allow_nosign=True,
    )
    public = await service.create(data)
    assert public.allow_nosign is True


@pytest.mark.asyncio
async def test_register_member_with_long_pin(service: MemberService):
    data = MemberCreate(
        name="Long Pin Member",
        pin="1234567890123456",  # max_length=16
        password="password123",
        ipaddress="192.168.1.25",
        report_url="http://localhost/reportlongpin",
        allow_nosign=False,
    )
    public = await service.create(data)
    internal = await service.repo.get(public.memberid)
    assert internal.pin.get_secret_value() == "1234567890123456"


@pytest.mark.asyncio
async def test_register_member_with_invalid_character_in_pin(service: MemberService):
    with pytest.raises(ValidationError):
        data = MemberCreate(
            name="Invalid Char Pin",
            pin="1234!@#$",  # invalid characters
            password="password123",
            ipaddress="192.168.1.26",
            report_url="http://localhost/reportcharpin",
            allow_nosign=False,
        )
        await service.create(data)


@pytest.mark.asyncio
async def test_register_member_with_only_numeric_name(service: MemberService):
    data = MemberCreate(
        name="123456",  # numeric name
        pin="123456",
        password="password123",
        ipaddress="192.168.1.27",
        report_url="http://localhost/reportnumericname",
        allow_nosign=False,
    )
    public = await service.create(data)
    assert public.name == "123456"


@pytest.mark.asyncio
async def test_update_member_pin(service: MemberService):
    data = MemberCreate(
        name="Pin Update Member",
        pin="123456",
        password="password123",
        ipaddress="192.168.1.28",
        report_url="http://localhost/reportpinupdate",
        allow_nosign=False,
    )
    public = await service.create(data)
    update = MemberUpdate(pin="654321")
    updated = await service.update(public.memberid, update)
    # Instead of public model, check internal model for pin
    internal = await service.repo.get(public.memberid)
    assert internal.pin.get_secret_value() == "654321"
    assert internal.password.get_secret_value() == "expected_password"


@pytest.mark.asyncio
async def test_update_member_password(service: MemberService):
    data = MemberCreate(
        name="Password Update Member",
        pin="123456",
        password="password123",
        ipaddress="192.168.1.29",
        report_url="http://localhost/reportpasswordupdate",
        allow_nosign=False,
    )
    public = await service.create(data)
    update = MemberUpdate(password="newpassword456")
    updated = await service.update(public.memberid, update)
    internal = await service.repo.get(public.memberid)
    assert internal.password.get_secret_value() == "newpassword456"


@pytest.mark.asyncio
async def test_register_member_with_valid_and_invalid_fields(service: MemberService):
    data = MemberCreate(
        name="Valid Name",
        pin="123456",
        password="password123",
        ipaddress="192.168.1.30",
        report_url="http://localhost/reportvalid",
        allow_nosign=False,
    )
    public = await service.create(data)

    # Update with invalid IP and valid name
    update = MemberUpdate(
        name="Updated Name",
        ipaddress="999.999.999.999",  # invalid IP
    )
    with pytest.raises(ValidationError):
        await service.update(public.memberid, update)

    # Update with valid IP and invalid name
    update = MemberUpdate(
        name="",
        ipaddress="192.168.1.31",
    )
    with pytest.raises(ValidationError):
        await service.update(public.memberid, update)

    # Update with valid name and IP
    update = MemberUpdate(
        name="Final Name",
        ipaddress="192.168.1.31",
    )
    updated = await service.update(public.memberid, update)
    assert updated.name == "Final Name"
    assert updated.ipaddress == "192.168.1.31"


@pytest.mark.asyncio
async def test_register_member_with_sql_injection(service: MemberService):
    data = MemberCreate(
        name="Robert'); DROP TABLE Members;--",
        pin="123456",
        password="password123",
        ipaddress="192.168.1.32",
        report_url="http://localhost/reportsql",
        allow_nosign=False,
    )
    public = await service.create(data)
    assert public.name == "Robert'); DROP TABLE Members;--"


@pytest.mark.asyncio
async def test_update_member_with_sql_injection(service: MemberService):
    data = MemberCreate(
        name="Jane Doe",
        pin="654321",
        password="password456",
        ipaddress="192.168.1.2",
        report_url="http://localhost/report2",
        allow_nosign=True,
    )
    public = await service.create(data)
    update = MemberUpdate(name="Robert'); DROP TABLE Members;--")
    updated = await service.update(public.memberid, update)
    assert updated.name == "Robert'); DROP TABLE Members;--"


@pytest.mark.asyncio
async def test_register_member_with_xss_attack(service: MemberService):
    data = MemberCreate(
        name="<script>alert('XSS')</script>",
        pin="123456",
        password="password123",
        ipaddress="192.168.1.33",
        report_url="http://localhost/reportxss",
        allow_nosign=False,
    )
    public = await service.create(data)
    assert public.name == "<script>alert('XSS')</script>"


@pytest.mark.asyncio
async def test_update_member_with_xss_attack(service: MemberService):
    data = MemberCreate(
        name="Jane Doe",
        pin="654321",
        password="password456",
        ipaddress="192.168.1.2",
        report_url="http://localhost/report2",
        allow_nosign=True,
    )
    public = await service.create(data)
    update = MemberUpdate(name="<script>alert('XSS')</script>")
    updated = await service.update(public.memberid, update)
    assert updated.name == "<script>alert('XSS')</script>"


@pytest.mark.asyncio
async def test_register_member_with_leading_trailing_spaces(service: MemberService):
    data = MemberCreate(
        name="   John Doe   ",  # leading and trailing spaces
        pin="123456",
        password="password123",
        ipaddress="192.168.1.34",
        report_url="http://localhost/reportspaces",
        allow_nosign=False,
    )
    public = await service.create(data)
    assert public.name == "John Doe"


@pytest.mark.asyncio
async def test_update_member_with_leading_trailing_spaces(service: MemberService):
    data = MemberCreate(
        name="Jane Doe",
        pin="654321",
        password="password456",
        ipaddress="192.168.1.2",
        report_url="http://localhost/report2",
        allow_nosign=True,
    )
    public = await service.create(data)
    update = MemberUpdate(name="   Jane Updated   ")
    updated = await service.update(public.memberid, update)
    assert updated.name == "Jane Updated"


@pytest.mark.asyncio
async def test_register_member_with_null_fields(service: MemberService):
    data = MemberCreate(
        name=None,
        pin="123456",
        password="password123",
        ipaddress="192.168.1.35",
        report_url="http://localhost/reportnull",
        allow_nosign=False,
    )
    with pytest.raises(ValidationError):
        await service.create(data)


@pytest.mark.asyncio
async def test_update_member_with_null_fields(service: MemberService):
    data = MemberCreate(
        name="Jane Doe",
        pin="654321",
        password="password456",
        ipaddress="192.168.1.2",
        report_url="http://localhost/report2",
        allow_nosign=True,
    )
    public = await service.create(data)
    update = MemberUpdate(name=None)
    updated = await service.update(public.memberid, update)
    assert updated.name is None


@pytest.mark.asyncio
async def test_register_member_with_empty_name(service: MemberService):
    with pytest.raises(ValidationError):
        data = MemberCreate(
            name="",
            pin="123456",
            password="password123",
            ipaddress="192.168.1.36",
            report_url="http://localhost/reportemptyname",
            allow_nosign=False,
        )
        await service.create(data)


@pytest.mark.asyncio
async def test_update_member_to_empty_name(service: MemberService):
    data = MemberCreate(
        name="Jane Doe",
        pin="654321",
        password="password456",
        ipaddress="192.168.1.2",
        report_url="http://localhost/report2",
        allow_nosign=True,
    )
    public = await service.create(data)
    update = MemberUpdate(name="")
    updated = await service.update(public.memberid, update)
    assert updated.name == ""


@pytest.mark.asyncio
async def test_register_member_with_non_ascii_characters(service: MemberService):
    data = MemberCreate(
        name="John Doe ñ",
        pin="123456",
        password="password123",
        ipaddress="192.168.1.37",
        report_url="http://localhost/reportnonascii",
        allow_nosign=False,
    )
    public = await service.create(data)
    assert public.name == "John Doe ñ"


@pytest.mark.asyncio
async def test_update_member_with_non_ascii_characters(service: MemberService):
    data = MemberCreate(
        name="Jane Doe",
        pin="654321",
        password="password456",
        ipaddress="192.168.1.2",
        report_url="http://localhost/report2",
        allow_nosign=True,
    )
    public = await service.create(data)
    update = MemberUpdate(name="Jane Doe ñ")
    updated = await service.update(public.memberid, update)
    assert updated.name == "Jane Doe ñ"


@pytest.mark.asyncio
async def test_register_member_with_very_long_name(service: MemberService):
    long_name = "A" * 256  # Exceeding typical max_length
    with pytest.raises(ValidationError):
        data = MemberCreate(
            name=long_name,
            pin="123456",
            password="password123",
            ipaddress="192.168.1.38",
            report_url="http://localhost/reportverylongname",
            allow_nosign=False,
        )
        await service.create(data)


@pytest.mark.asyncio
async def test_update_member_to_very_long_name(service: MemberService):
    data = MemberCreate(
        name="Jane Doe",
        pin="654321",
        password="password456",
        ipaddress="192.168.1.2",
        report_url="http://localhost/report2",
        allow_nosign=True,
    )
    public = await service.create(data)
    long_name = "B" * 256  # Exceeding typical max_length
    with pytest.raises(ValidationError):
        update = MemberUpdate(name=long_name)
        await service.update(public.memberid, update)


@pytest.mark.asyncio
async def test_register_member_with_valid_ip_and_url(service: MemberService):
    data = MemberCreate(
        name="Valid IP and URL",
        pin="123456",
        password="password123",
        ipaddress="192.168.1.39",
        report_url="http://localhost/reportvalidipurl",
        allow_nosign=False,
    )
    public = await service.create(data)
    assert public.ipaddress == "192.168.1.39"
    assert public.report_url == "http://localhost/reportvalidipurl"


@pytest.mark.asyncio
async def test_update_member_ipaddress_and_report_url(service: MemberService):
    data = MemberCreate(
        name="Update IP and URL",
        pin="123456",
        password="password123",
        ipaddress="192.168.1.40",
        report_url="http://localhost/reportupdateipurl",
        allow_nosign=False,
    )
    public = await service.create(data)
    update = MemberUpdate(
        ipaddress="192.168.1.41",
        report_url="http://localhost/newreportupdateurl",
    )
    updated = await service.update(public.memberid, update)
    assert updated.ipaddress == "192.168.1.41"
    assert updated.report_url == "http://localhost/newreportupdateurl"


@pytest.mark.asyncio
async def test_register_member_with_optional_fields(service: MemberService):
    data = MemberCreate(
        name="Optional Fields Member",
        pin="123456",
        password="password123",
        ipaddress="192.168.1.42",
        report_url="http://localhost/reportoptional",
        allow_nosign=True,
    )
    public = await service.create(data)
    assert public.name == "Optional Fields Member"
    assert public.allow_nosign is True


@pytest.mark.asyncio
async def test_update_member_optional_fields(service: MemberService):
    data = MemberCreate(
        name="Member With Options",
        pin="123456",
        password="password123",
        ipaddress="192.168.1.43",
        report_url="http://localhost/reportwithoptions",
        allow_nosign=True,
    )
    public = await service.create(data)
    update = MemberUpdate(allow_nosign=False)
    updated = await service.update(public.memberid, update)
    assert updated.allow_nosign is False


@pytest.mark.asyncio
async def test_register_member_with_empty_pin(service: MemberService):
    with pytest.raises(ValidationError):
        data = MemberCreate(
            name="No Pin Member",
            pin="",
            password="password123",
            ipaddress="192.168.1.44",
            report_url="http://localhost/reportnopin",
            allow_nosign=False,
        )
        await service.create(data)


@pytest.mark.asyncio
async def test_update_member_pin_to_empty(service: MemberService):
    data = MemberCreate(
        name="Jane Doe",
        pin="654321",
        password="password456",
        ipaddress="192.168.1.2",
        report_url="http://localhost/report2",
        allow_nosign=True,
    )
    public = await service.create(data)
    update = MemberUpdate(pin="")
    updated = await service.update(public.memberid, update)
    internal = await service.repo.get(public.memberid)
    assert internal.pin.get_secret_value() == ""


@pytest.mark.asyncio
async def test_register_member_with_empty_password(service: MemberService):
    with pytest.raises(ValidationError):
        data = MemberCreate(
            name="No Password Member",
            pin="123456",
            password="",
            ipaddress="192.168.1.45",
            report_url="http://localhost/reportnopassword",
            allow_nosign=False,
        )
        await service.create(data)


@pytest.mark.asyncio
async def test_update_member_password_to_empty(service: MemberService):
    data = MemberCreate(
        name="Jane Doe",
        pin="654321",
        password="password456",
        ipaddress="192.168.1.2",
        report_url="http://localhost/report2",
        allow_nosign=True,
    )
    public = await service.create(data)
    update = MemberUpdate(password="")
    updated = await service.update(public.memberid, update)
    internal = await service.repo.get(public.memberid)
    assert internal.password.get_secret_value() == ""


@pytest.mark.asyncio
async def test_register_member_with_ipaddress_as_name(service: MemberService):
    data = MemberCreate(
        name="192.168.1.46",  # IP address format
        pin="123456",
        password="password123",
        ipaddress="192.168.1.46",
        report_url="http://localhost/reportipaddressasname",
        allow_nosign=False,
    )
    public = await service.create(data)
    assert public.name == "192.168.1.46"


@pytest.mark.asyncio
async def test_update_member_name_to_ipaddress(service: MemberService):
    data = MemberCreate(
        name="Jane Doe",
        pin="654321",
        password="password456",
        ipaddress="192.168.1.2",
        report_url="http://localhost/report2",
        allow_nosign=True,
    )
    public = await service.create(data)
    update = MemberUpdate(name="192.168.1.47")
    updated = await service.update(public.memberid, update)
    assert updated.name == "192.168.1.47"


@pytest.mark.asyncio
async def test_register_member_with_url_containing_spaces(service: MemberService):
    with pytest.raises(ValidationError):
        data = MemberCreate(
            name="Invalid URL Member",
            pin="123456",
            password="password123",
            ipaddress="192.168.1.48",
            report_url="http://localhost/invalid url",
            allow_nosign=False,
        )
        await service.create(data)


@pytest.mark.asyncio
async def test_update_member_report_url_with_spaces(service: MemberService):
    data = MemberCreate(
        name="Jane Doe",
        pin="654321",
        password="password456",
        ipaddress="192.168.1.2",
        report_url="http://localhost/report2",
        allow_nosign=True,
    )
    public = await service.create(data)
    update = MemberUpdate(report_url="http://localhost/new url")
    updated = await service.update(public.memberid, update)
    assert updated.report_url == "http://localhost/new url"


@pytest.mark.asyncio
async def test_register_member_with_port_in_ipaddress(service: MemberService):
    data = MemberCreate(
        name="Port In IP Member",
        pin="123456",
        password="password123",
        ipaddress="192.168.1.49:8000",  # IP with port
        report_url="http://localhost/reportportinip",
        allow_nosign=False,
    )
    public = await service.create(data)
    assert public.ipaddress == "192.168.1.49:8000"


@pytest.mark.asyncio
async def test_update_member_ipaddress_with_port(service: MemberService):
    data = MemberCreate(
        name="Jane Doe",
        pin="654321",
        password="password456",
        ipaddress="192.168.1.2",
        report_url="http://localhost/report2",
        allow_nosign=True,
    )
    public = await service.create(data)
    update = MemberUpdate(ipaddress="192.168.1.50:8000")
    updated = await service.update(public.memberid, update)
    assert updated.ipaddress == "192.168.1.50:8000"


@pytest.mark.asyncio
async def test_register_member_with_subnet_ipaddress(service: MemberService):
    data = MemberCreate(
        name="Subnet IP Member",
        pin="123456",
        password="password123",
        ipaddress="192.168.1.0/24",  # Subnet format
        report_url="http://localhost/reportsubnetip",
        allow_nosign=False,
    )
    public = await service.create(data)
    assert public.ipaddress == "192.168.1.0/24"


@pytest.mark.asyncio
async def test_update_member_ipaddress_to_subnet(service: MemberService):
    data = MemberCreate(
        name="Jane Doe",
        pin="654321",
        password="password456",
        ipaddress="192.168.1.2",
        report_url="http://localhost/report2",
        allow_nosign=True,
    )
    public = await service.create(data)
    update = MemberUpdate(ipaddress="192.168.1.0/24")
    updated = await service.update(public.memberid, update)
    assert updated.ipaddress == "192.168.1.0/24"


@pytest.mark.asyncio
async def test_register_member_with_empty_report_url(service: MemberService):
    with pytest.raises(ValidationError):
        data = MemberCreate(
            name="No URL Member",
            pin="123456",
            password="password123",
            ipaddress="192.168.1.51",
            report_url="",
            allow_nosign=False,
        )
        await service.create(data)


@pytest.mark.asyncio
async def test_update_member_report_url_to_empty(service: MemberService):
    data = MemberCreate(
        name="Jane Doe",
        pin="654321",
        password="password456",
        ipaddress="192.168.1.2",
        report_url="http://localhost/report2",
        allow_nosign=True,
    )
    public = await service.create(data)
    update = MemberUpdate(report_url="")
    updated = await service.update(public.memberid, update)
    assert updated.report_url == ""


@pytest.mark.asyncio
async def test_register_member_with_non_existent_ip(service: MemberService):
    data = MemberCreate(
        name="Non Existent IP",
        pin="123456",
        password="password123",
        ipaddress="10.255.255.1",  # Assuming this IP does not exist in the network
        report_url="http://localhost/reportnonexistentip",
        allow_nosign=False,
    )
    public = await service.create(data)
    assert public.ipaddress == "10.255.255.1"


@pytest.mark.asyncio
async def test_update_member_ipaddress_to_non_existent_ip(service: MemberService):
    data = MemberCreate(
        name="Jane Doe",
        pin="654321",
        password="password456",
        ipaddress="192.168.1.2",
        report_url="http://localhost/report2",
        allow_nosign=True,
    )
    public = await service.create(data)
    update = MemberUpdate(ipaddress="10.255.255.2")
    updated = await service.update(public.memberid, update)
    assert updated.ipaddress == "10.255.255.2"


@pytest.mark.asyncio
async def test_register_member_with_both_sign_and_nosign(service: MemberService):
    data = MemberCreate(
        name="Sign and NoSign",
        pin="123456",
        password="password123",
        ipaddress="192.168.1.52",
        report_url="http://localhost/reportbothsignnosign",
        allow_nosign=True,
    )
    public = await service.create(data)
    assert public.allow_nosign is True


@pytest.mark.asyncio
async def test_update_member_allow_nosign_to_false(service: MemberService):
    data = MemberCreate(
        name="Jane Doe",
        pin="654321",
        password="password456",
        ipaddress="192.168.1.2",
        report_url="http://localhost/report2",
        allow_nosign=True,
    )
    public = await service.create(data)
    update = MemberUpdate(allow_nosign=False)
    updated = await service.update(public.memberid, update)
    assert updated.allow_nosign is False


@pytest.mark.asyncio
async def test_register_member_with_invalid_json_fields(service: MemberService):
    with pytest.raises(ValidationError):
        data = MemberCreate(
            name={"invalid": "json"},  # Invalid type
            pin="123456",
            password="password123",
            ipaddress="192.168.1.53",
            report_url="http://localhost/reportinvalidjson",
            allow_nosign=False,
        )
        await service.create(data)


@pytest.mark.asyncio
async def test_update_member_with_invalid_json_fields(service: MemberService):
    data = MemberCreate(
        name="Jane Doe",
        pin="654321",
        password="password456",
        ipaddress="192.168.1.2",
        report_url="http://localhost/report2",
        allow_nosign=True,
    )
    public = await service.create(data)
    update = MemberUpdate(name={"invalid": "json"})  # Invalid type
    with pytest.raises(ValidationError):
        await service.update(public.memberid, update)


@pytest.mark.asyncio
async def test_register_member_with_sql_injection_in_pin(service: MemberService):
    data = MemberCreate(
        name="Valid Name",
        pin="1234'; DROP TABLE Members;--",  # SQL injection in pin
        password="password123",
        ipaddress="192.168.1.54",
        report_url="http://localhost/reportvalidsqlpin",
        allow_nosign=False,
    )
    public = await service.create(data)
    internal = await service.repo.get(public.memberid)
    assert internal.pin.get_secret_value() == "1234'; DROP TABLE Members;--"


@pytest.mark.asyncio
async def test_update_member_pin_with_sql_injection(service: MemberService):
    data = MemberCreate(
        name="Jane Doe",
        pin="654321",
        password="password456",
        ipaddress="192.168.1.2",
        report_url="http://localhost/report2",
        allow_nosign=True,
    )
    public = await service.create(data)
    update = MemberUpdate(pin="1234'; DROP TABLE Members;--")  # SQL injection
    updated = await service.update(public.memberid, update)
    internal = await service.repo.get(public.memberid)
    assert internal.pin.get_secret_value() == "1234'; DROP TABLE Members;--"


@pytest.mark.asyncio
async def test_register_member_with_xss_injection_in_name(service: MemberService):
    data = MemberCreate(
        name="<img src='x' onerror='alert(1)'>",  # XSS in name
        pin="123456",
        password="password123",
        ipaddress="192.168.1.55",
        report_url="http://localhost/reportxssname",
        allow_nosign=False,
    )
    public = await service.create(data)
    assert public.name == "<img src='x' onerror='alert(1)'>"
