"""member service using database."""

from app.models.member import Member
from app.repositories.persistance.db_repo_member import MemberRepository
from app.schemas.sch_member import MemberCreate, MemberPublic, MemberUpdate


class MemberService:
    def __init__(self, repo: MemberRepository):
        self.repo = repo

    async def create_member(self, member_data: MemberCreate) -> MemberPublic:
        member = Member(**member_data.model_dump())
        created = await self.repo.add(member)
        return MemberPublic.model_validate(created)

    async def get_member(self, memberid: str) -> MemberPublic:
        member = await self.repo.get(memberid)
        return MemberPublic.model_validate(member)

    async def update_member(
        self, memberid: str, update_data: MemberUpdate
    ) -> MemberPublic:
        updated = await self.repo.update(
            memberid, **update_data.model_dump(exclude_unset=True)
        )
        return MemberPublic.model_validate(updated)

    async def delete_member(self, memberid: str):
        await self.repo.remove(memberid)

    async def list_members(self) -> list[MemberPublic]:
        members = await self.repo.all()
        return [MemberPublic.model_validate(m) for m in members]
