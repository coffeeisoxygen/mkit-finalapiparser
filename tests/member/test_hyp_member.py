# tests/test_member_service.py
# pyright: reportArgumentType=false

import pydantic
from app.repositories.rep_member import InMemoryMemberRepository
from app.service.srv_member import MemberCreate, MemberService
from hypothesis import given
from hypothesis import strategies as st

# =======================
# Helper strategies
# =======================
valid_url = st.from_regex(
    r"https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[a-zA-Z0-9._-]*)*",
    fullmatch=True,
)


# =======================
# 1. VALID CASES
# =======================
@given(
    name=st.text(min_size=1, max_size=100),
    pin=st.text(min_size=6, max_size=6),
    password=st.text(min_size=6, max_size=20),
    ipaddress=st.ip_addresses(),
    report_url=valid_url,
    allow_nosign=st.booleans(),
)
def test_register_member_hypothesis_valid(
    name, pin, password, ipaddress, report_url, allow_nosign
):
    repo = InMemoryMemberRepository()
    service = MemberService(repo)

    data = MemberCreate(
        name=name,
        pin=pin,
        password=password,
        ipaddress=ipaddress,
        report_url=report_url,
        allow_nosign=allow_nosign,
    )
    public = service.create_member(data)

    assert public.name == name
    assert len(public.memberid) > 0


# =======================
# 2. INVALID / MIXED CASES
# =======================
@given(
    name=st.one_of(st.text(min_size=1, max_size=100), st.text(max_size=0)),
    pin=st.one_of(st.text(min_size=6, max_size=6), st.text(max_size=3)),
    password=st.one_of(st.text(min_size=6, max_size=20), st.text(max_size=3)),
    ipaddress=st.one_of(st.ip_addresses(), st.text()),  # bisa valid ip atau sampah
    report_url=st.one_of(valid_url, st.text()),  # bisa valid url atau sampah
    allow_nosign=st.booleans(),
)
def test_register_member_hypothesis_mixed(
    name, pin, password, ipaddress, report_url, allow_nosign
):
    repo = InMemoryMemberRepository()
    service = MemberService(repo)

    try:
        data = MemberCreate(
            name=name,
            pin=pin,
            password=password,
            ipaddress=ipaddress,
            report_url=report_url,
            allow_nosign=allow_nosign,
        )
        public = service.create_member(data)
        assert public.name == name
    except pydantic.ValidationError:
        # expected fail
        pass
