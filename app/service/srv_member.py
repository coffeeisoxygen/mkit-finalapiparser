"""Service layer untuk Member."""

from app.repositories.rep_member import InMemoryMemberRepository
from app.schemas.sch_member import (
    MemberCreate,
    MemberDelete,
    MemberPublic,
    MemberUpdate,
)


class MemberService:
    """Business logic untuk Member."""

    def __init__(self, repo: InMemoryMemberRepository):
        self.repo = repo

    def register(self, data: MemberCreate) -> MemberPublic:
        """Register member baru."""
        member = self.repo.create(data)
        return MemberPublic(**member.model_dump())

    def update(self, memberid: str, data: MemberUpdate) -> MemberPublic:
        """Update member."""
        member = self.repo.get(memberid)
        if not member:
            raise KeyError(f"Member {memberid} tidak ditemukan.")

        update_data = data.model_dump(exclude_unset=True)
        updated = member.model_copy(update=update_data)
        self.repo.update(memberid, updated)
        return MemberPublic(**updated.model_dump())

    def delete(self, data: MemberDelete) -> None:
        """Hapus member berdasarkan ID."""
        self.repo.remove(data.memberid)

    def list_members(self) -> list[MemberPublic]:
        """Ambil semua member publik."""
        return [MemberPublic(**m.model_dump()) for m in self.repo.all()]
