"""Member service: business logic untuk Member."""

from app.custom.cst_exceptions import EntityExcError
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
        nomor_urut = len(self.repo.all()) + 1
        memberid = f"MKIT{str(nomor_urut).zfill(3)}"
        if self.repo.get(memberid):
            raise EntityExcError(f"Member dengan ID {memberid} sudah terdaftar.")
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
        return MemberPublic(**member.model_dump(exclude={"pin", "password"}))

    def get(self, memberid: str) -> MemberPublic | None:
        """Ambil member by id."""
        m = self.repo.get(memberid)
        if not m:
            raise EntityExcError(f"Member dengan ID {memberid} tidak ditemukan.")
        return MemberPublic(**m.model_dump(exclude={"pin", "password"}))

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
            raise EntityExcError(f"Member dengan ID {memberid} tidak ditemukan.")

        updated_data = member.model_copy(update=data.model_dump(exclude_unset=True))
        self.repo.update(memberid, updated_data)
        return MemberPublic(**updated_data.model_dump(exclude={"pin", "password"}))

    def remove(self, memberid: str) -> None:
        """Hapus member."""
        member = self.repo.get(memberid)
        if not member:
            raise EntityExcError(f"Member dengan ID {memberid} tidak ditemukan.")
        self.repo.remove(memberid)
