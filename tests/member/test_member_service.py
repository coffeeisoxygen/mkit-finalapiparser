# tests/test_member_service.py
from ipaddress import IPv4Address  # add this import

import pytest
from app.repositories.rep_member import InMemoryMemberRepository
from app.schemas.sch_member import MemberCreate, MemberUpdate
from app.service.srv_member import MemberService
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
