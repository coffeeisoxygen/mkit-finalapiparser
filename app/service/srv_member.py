"""Member service: business logic untuk Member."""

import re

from app.repositories.base_repo import AbstractRepository
from app.schemas.sch_member import (
    MemberCreate,
    MemberInDB,
    MemberPublic,
    MemberUpdate,
)


class MemberService:
    """Service untuk mengelola member."""

    def __init__(self, repo: AbstractRepository[MemberInDB, str]):
        self.repo = repo

    def register(self, data: MemberCreate) -> MemberPublic:
        """Daftarkan member baru."""
        base_id = re.sub(r"[^a-zA-Z0-9]", "", data.name.upper())[:5]
        memberid = base_id + "001"
        member = MemberInDB(
            memberid=memberid,
            name=data.name,
            pin=data.pin,
            password=data.password,
            ipaddress=data.ipaddress,
            report_url=data.report_url,
            allow_nosign=data.allow_nosign,
            is_active=True,
        )
        self.repo.add(member.memberid, member)
        return MemberPublic(**member.dict(exclude={"pin", "password"}))

    def get(self, memberid: str) -> MemberPublic | None:
        """Ambil member by id."""
        m = self.repo.get(memberid)
        if not m:
            return None
        return MemberPublic(**m.dict(exclude={"pin", "password"}))

    def list_members(self) -> list[MemberPublic]:
        """Ambil semua member."""
        return [
            MemberPublic(**m.model_dump(exclude={"pin", "password"}))
            for m in self.repo.all()
        ]

    def update(self, memberid: str, data: MemberUpdate) -> MemberPublic:
        """Update data member."""
        member = self.repo.get(memberid)
        if not member:
            raise KeyError(f"Member {memberid} tidak ditemukan.")

        updated_data = member.copy(update=data.dict(exclude_unset=True))
        self.repo.update(memberid, updated_data)
        return MemberPublic(**updated_data.dict(exclude={"pin", "password"}))

    def remove(self, memberid: str) -> None:
        """Hapus member."""
        self.repo.remove(memberid)
