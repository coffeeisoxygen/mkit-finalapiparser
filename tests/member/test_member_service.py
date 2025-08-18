# tests/test_member_service.py
from ipaddress import IPv4Address  # add this import

import pytest
from app.custom.exceptions import EntityAlreadyExistsError, EntityNotFoundError
from app.repositories.rep_member import InMemoryMemberRepository
from app.schemas.sch_member import MemberCreate, MemberUpdate
from app.service.srv_member import MemberDelete, MemberService
from hypothesis import given
from hypothesis import strategies as st


@pytest.fixture
def service():
    return MemberService(InMemoryMemberRepository())


@given(name=st.text(min_size=1, max_size=10))
def test_create_member(name):
    service = MemberService(InMemoryMemberRepository())
    data = MemberCreate(
        name=name,
        pin="123456",
        password="123456",
        ipaddress=IPv4Address("192.168.1.1"),
        report_url="http://example.com/report",  # type: ignore
        allow_nosign=False,
    )
    member = service.create_member(data)

    assert member.memberid is not None
    assert member.name == name


@given(name=st.text(min_size=1, max_size=10))
def test_update_member(name):
    service = MemberService(InMemoryMemberRepository())
    member = service.create_member(
        MemberCreate(
            name="old",
            pin="123456",
            password="123456",
            ipaddress=IPv4Address("192.168.1.1"),
            report_url="http://example.com/report",  # type: ignore
            allow_nosign=False,
        )
    )
    updated = service.update_member(member.memberid, MemberUpdate(name=name))

    assert updated.name == name


def test_create_duplicate_member():
    service = MemberService(InMemoryMemberRepository())
    data = MemberCreate(
        name="dup",
        pin="123456",
        password="123456",
        ipaddress=IPv4Address("192.168.1.1"),
        report_url="http://example.com",  # use valid AnyHttpUrl # type: ignore
        allow_nosign=False,
    )
    service.create_member(data)
    # simulate duplicate by creating another member with same data
    with pytest.raises(EntityAlreadyExistsError):
        service.create_member(data)


def test_get_nonexistent_member():
    service = MemberService(InMemoryMemberRepository())
    with pytest.raises(EntityNotFoundError):
        service.get_member("MEM999")


def test_update_nonexistent_member():
    service = MemberService(InMemoryMemberRepository())
    with pytest.raises(EntityNotFoundError):
        service.update_member("MEM999", MemberUpdate(name="new"))


def test_remove_nonexistent_member():
    service = MemberService(InMemoryMemberRepository())
    with pytest.raises(EntityNotFoundError):
        service.remove_member(MemberDelete(memberid="MEM999"))


def test_remove_existing_member():
    service = MemberService(InMemoryMemberRepository())
    member = service.create_member(
        MemberCreate(
            name="toremove",
            pin="123456",
            password="123456",
            ipaddress=IPv4Address("192.168.1.1"),
            report_url="http://example.com/report",  # type: ignore
            allow_nosign=False,
        )
    )
    service.remove_member(MemberDelete(memberid=member.memberid))
    with pytest.raises(EntityNotFoundError):
        service.get_member(member.memberid)


def test_list_members_count():
    service = MemberService(InMemoryMemberRepository())
    for i in range(3):
        service.create_member(
            MemberCreate(
                name=f"name{i}",
                pin="123456",
                password="123456",
                ipaddress=IPv4Address("192.168.1.1"),
                report_url="http://example.com/report",  # type: ignore
                allow_nosign=False,
            )
        )
    members = service.list_members()
    assert len(members) == 3
    assert len(members) == 3
