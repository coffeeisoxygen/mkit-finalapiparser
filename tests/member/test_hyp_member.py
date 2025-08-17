import pytest
from app.repositories.rep_member import InMemoryMemberRepository
from app.service.srv_member import MemberCreate, MemberService
from hypothesis import given
from hypothesis import strategies as st


@given(
    st.text(min_size=1, max_size=100),
    st.text(min_size=6, max_size=6),
    st.text(min_size=6, max_size=20),
    st.ip_addresses(),
    st.from_regex(r"https?://[a-zA-Z0-9.-]+(?:/[a-zA-Z0-9._-]*)*", fullmatch=True),
    st.booleans(),
)
def test_register_member_hypothesis(
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
    public = service.register(data)
    assert public.name == name


# Edge case: Empty name, pin, password, invalid IP, invalid URL
@pytest.mark.parametrize(
    "name, pin, password, ipaddress, report_url, allow_nosign",
    [
        ("", "123456", "abcdef", "0.0.0.0", "http://valid-url.com", True),  # empty name
        (
            "EdgeUser",
            "",
            "abcdef",
            "127.0.0.1",
            "http://valid-url.com",
            False,
        ),  # empty pin
        (
            "EdgeUser",
            "123456",
            "",
            "127.0.0.1",
            "http://valid-url.com",
            True,
        ),  # empty password
        (
            "EdgeUser",
            "123456",
            "abcdef",
            "999.999.999.999",
            "http://valid-url.com",
            False,
        ),  # invalid IP
        ("EdgeUser", "123456", "abcdef", "127.0.0.1", "not-a-url", True),  # invalid URL
        (
            "A" * 100,
            "1" * 6,
            "p" * 20,
            "255.255.255.255",
            "https://max-url.com/path",
            False,
        ),  # max lengths
        ("B", "123456", "abcdef", "::1", "http://ipv6.com", True),  # IPv6
    ],
)
def test_register_member_edge_cases(
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
        public = service.register(data)
        assert public.name == name
    except Exception:
        # Expecting failure for invalid cases
        assert (
            not name
            or not pin
            or not password
            or ipaddress == "999.999.999.999"
            or report_url == "not-a-url"
        )
