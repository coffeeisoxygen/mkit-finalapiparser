# pyright: reportArgumentType= false

import pytest
from app.repositories.rep_member import InMemoryMemberRepository
from app.schemas.sch_member import MemberCreate, MemberUpdate
from app.service.srv_member import MemberService


@pytest.fixture
def service():
    repo = InMemoryMemberRepository()
    return MemberService(repo)


def test_register_and_get_member(service: MemberService):
    data = MemberCreate(
        name="John Doe",
        pin="123456",
        password="password123",
        ipaddress="192.168.1.1",
        report_url="http://localhost/report",
        allow_nosign=False,
    )
    public = service.register(data)
    assert public.name == "John Doe"
    assert public.memberid.startswith("JOHND")

    fetched = service.get(public.memberid)
    assert fetched is not None
    assert fetched.name == "John Doe"


def test_update_member(service: MemberService):
    data = MemberCreate(
        name="Jane Doe",
        pin="654321",
        password="password456",
        ipaddress="192.168.1.2",
        report_url="http://localhost/report2",
        allow_nosign=True,
    )
    public = service.register(data)
    update = MemberUpdate(name="Jane Updated")
    updated = service.update(public.memberid, update)
    assert updated.name == "Jane Updated"


def test_remove_member(service: MemberService):
    data = MemberCreate(
        name="Remove Me",
        pin="111111",
        password="password789",
        ipaddress="192.168.1.3",
        report_url="http://localhost/report3",
        allow_nosign=False,
    )
    public = service.register(data)
    service.remove(public.memberid)
    assert service.get(public.memberid) is None


def test_register_duplicate_member(service: MemberService):
    data = MemberCreate(
        name="Dup Name",
        pin="222222",
        password="dup123",
        ipaddress="192.168.1.4",
        report_url="http://localhost/report4",
        allow_nosign=True,
    )
    public1 = service.register(data)
    # Attempt to register with same pin, should raise or handle duplicate
    with pytest.raises(Exception):
        service.register(data)


def test_update_nonexistent_member(service: MemberService):
    update = MemberUpdate(name="Ghost")
    # Should not update, returns None or raises
    with pytest.raises(Exception):
        service.update("NONEXISTENT_ID", update)


def test_remove_nonexistent_member(service: MemberService):
    # Should not remove, returns None or raises
    with pytest.raises(Exception):
        service.remove("NONEXISTENT_ID")


def test_register_member_with_empty_fields(service: MemberService):
    data = MemberCreate(
        name="",
        pin="",
        password="",
        ipaddress="",
        report_url="",
        allow_nosign=False,
    )
    with pytest.raises(Exception):
        service.register(data)
