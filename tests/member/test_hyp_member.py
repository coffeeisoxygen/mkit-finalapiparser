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
