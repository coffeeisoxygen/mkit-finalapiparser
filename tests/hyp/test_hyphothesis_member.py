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
memberid_strategy = st.text(min_size=1, max_size=20)
name_strategy = st.text(min_size=1, max_size=50)


@given(memberid=memberid_strategy, name=name_strategy)
@pytest.mark.asyncio
async def test_create_and_get_member(service, memberid, name):
    data = MemberCreate(memberid=memberid, name=name)
    created = await service.create(data)

    assert created.memberid == memberid
    assert created.name == name

    fetched = await service.get(memberid)
    assert fetched == created


@given(memberid=memberid_strategy, name=name_strategy)
@pytest.mark.asyncio
async def test_update_member(service, memberid, name):
    # create dulu
    created = await service.create(MemberCreate(memberid=memberid, name="dummy"))

    # update
    updated = await service.update(memberid, MemberUpdate(name=name))
    assert updated.name == name


@given(memberid=memberid_strategy, name=name_strategy)
@pytest.mark.asyncio
async def test_delete_member(service, memberid, name):
    # create
    await service.create(MemberCreate(memberid=memberid, name=name))

    # delete
    await service.remove(MemberDelete(memberid=memberid))

    # pastikan not found
    with pytest.raises(Exception):
        await service.get(memberid)
