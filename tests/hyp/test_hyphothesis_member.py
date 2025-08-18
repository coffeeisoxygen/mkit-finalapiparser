import pytest
from app.repositories.rep_member import AsyncInMemoryMemberRepo
from app.schemas.sch_member import MemberCreate, MemberDelete, MemberUpdate
from app.service.srv_member import MemberService
from hypothesis import given
from hypothesis import strategies as st


@pytest.fixture
def service():
    repo = AsyncInMemoryMemberRepo()
    return MemberService(repo)


# strategi generate data untuk member
name_strategy = st.text(min_size=1, max_size=50)
pin_strategy = st.text(min_size=6, max_size=6)
password_strategy = st.text(min_size=8, max_size=20)
ipaddress_strategy = st.just("192.168.1.100")
report_url_strategy = st.just("http://localhost/report")
allow_nosign_strategy = st.just(False)


@given(
    name=name_strategy,
    pin=pin_strategy,
    password=password_strategy,
    ipaddress=ipaddress_strategy,
    report_url=report_url_strategy,
    allow_nosign=allow_nosign_strategy,
)
@pytest.mark.asyncio
async def test_create_and_get_member(
    service, name, pin, password, ipaddress, report_url, allow_nosign
):
    data = MemberCreate(
        name=name,
        pin=pin,
        password=password,
        ipaddress=ipaddress,
        report_url=report_url,
        allow_nosign=allow_nosign,
    )
    created = await service.create_member(data)

    assert created.name == name

    fetched = await service.get_member(created.memberid)
    assert fetched == created


@given(
    name=name_strategy,
    pin=pin_strategy,
    password=password_strategy,
    ipaddress=ipaddress_strategy,
    report_url=report_url_strategy,
    allow_nosign=allow_nosign_strategy,
)
@pytest.mark.asyncio
async def test_update_member(
    service, name, pin, password, ipaddress, report_url, allow_nosign
):
    # create dulu
    created = await service.create_member(
        MemberCreate(
            name="dummy",
            pin=pin,
            password=password,
            ipaddress=ipaddress,
            report_url=report_url,
            allow_nosign=allow_nosign,
        )
    )

    # update
    updated = await service.update_member(created.memberid, MemberUpdate(name=name))
    assert updated.name == name


@given(
    name=name_strategy,
    pin=pin_strategy,
    password=password_strategy,
    ipaddress=ipaddress_strategy,
    report_url=report_url_strategy,
    allow_nosign=allow_nosign_strategy,
)
@pytest.mark.asyncio
async def test_delete_member(
    service, name, pin, password, ipaddress, report_url, allow_nosign
):
    # create
    created = await service.create_member(
        MemberCreate(
            name=name,
            pin=pin,
            password=password,
            ipaddress=ipaddress,
            report_url=report_url,
            allow_nosign=allow_nosign,
        )
    )

    # delete
    await service.remove_member(MemberDelete(memberid=created.memberid))

    # pastikan not found
    with pytest.raises(Exception):
        await service.get_member(created.memberid)
