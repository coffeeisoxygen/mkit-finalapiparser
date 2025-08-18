from app.custom.exceptions import EntityAlreadyExistsError, EntityNotFoundError
from app.mlogg import logger
from app.repositories.rep_member import AsyncInMemoryMemberRepo
from app.schemas.sch_member import (
    MemberCreate,
    MemberDelete,
    MemberInDB,
    MemberPublic,
    MemberUpdate,
)

PREFIX_MEMBER = "MEM"


class MemberService:
    def __init__(self, repo: AsyncInMemoryMemberRepo):
        self.repo = repo
        self._counter = 0

    def _next_id(self) -> str:
        """Generate incremental member ID."""
        self._counter += 1
        return f"{PREFIX_MEMBER}{str(self._counter).zfill(3)}"

    # CREATE
    async def create_member(self, data: MemberCreate) -> MemberPublic:
        for member in await self.repo.all():
            if member.name == data.name:
                raise EntityAlreadyExistsError(
                    f"Member with name '{data.name}' already exists"
                )

        memberid = self._next_id()
        log = logger.bind(operation="create_member", memberid=memberid)

        if await self.repo.get(memberid):
            log.error("Member already exists")
            raise EntityAlreadyExistsError(context={"memberid": memberid})

        member = MemberInDB.from_create(memberid, data)
        await self.repo.add(memberid, member)
        log.info("Member created successfully")
        return MemberPublic(**member.model_dump())

    # READ
    async def get_member(self, memberid: str) -> MemberPublic:
        log = logger.bind(operation="get_member", memberid=memberid)
        member = await self.repo.get(memberid)
        if not member:
            log.error("Member not found")
            raise EntityNotFoundError(context={"memberid": memberid})
        log.info("Member retrieved")
        return MemberPublic(**member.model_dump())

    # UPDATE
    async def update_member(self, memberid: str, data: MemberUpdate) -> MemberPublic:
        log = logger.bind(operation="update_member", memberid=memberid)
        member = await self.repo.get(memberid)
        if not member:
            log.error("Member not found for update")
            raise EntityNotFoundError(context={"memberid": memberid})

        member.update_from(data)
        await self.repo.update(memberid, member)
        log.info("Member updated successfully")
        return MemberPublic(**member.model_dump())

    # DELETE
    async def remove_member(self, data: MemberDelete) -> None:
        log = logger.bind(operation="remove_member", memberid=data.memberid)
        member = await self.repo.get(data.memberid)
        if not member:
            log.error("Member not found for deletion")
            raise EntityNotFoundError(context={"memberid": data.memberid})
        await self.repo.remove(data.memberid)
        log.info("Member removed successfully")

    # LIST
    async def list_members(self) -> list[MemberPublic]:
        log = logger.bind(operation="list_members")
        members = [MemberPublic(**m.model_dump()) for m in await self.repo.all()]
        log.info("Listed all members", count=len(members))
        return members
