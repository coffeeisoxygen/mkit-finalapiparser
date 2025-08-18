from app.custom.exceptions import EntityAlreadyExistsError, EntityNotFoundError
from app.mlogg import logger
from app.repositories.rep_member import InMemoryMemberRepository
from app.schemas.sch_member import (
    MemberCreate,
    MemberDelete,
    MemberInDB,
    MemberPublic,
    MemberUpdate,
)

PREFIX_MEMBER = "MEM"


class MemberService:
    def __init__(self, repo: InMemoryMemberRepository):
        self.repo = repo
        self._counter = 0

    def _next_id(self) -> str:
        self._counter += 1
        return f"{PREFIX_MEMBER}{str(self._counter).zfill(3)}"

    # CREATE
    def create_member(self, data: MemberCreate) -> MemberPublic:
        memberid = self._next_id()
        log = logger.bind(operation="create_member", memberid=memberid)

        if self.repo.get(memberid):
            log.error("Member already exists")
            raise EntityAlreadyExistsError(context={"memberid": memberid})

        member = MemberInDB.from_create(memberid, data)
        self.repo.add(memberid, member)
        log.info("Member created successfully")
        return MemberPublic(**member.model_dump())

    # READ
    def get_member(self, memberid: str) -> MemberPublic:
        log = logger.bind(operation="get_member", memberid=memberid)
        member = self.repo.get(memberid)
        if not member:
            log.error("Member not found")
            raise EntityNotFoundError(context={"memberid": memberid})
        log.info("Member retrieved")
        return MemberPublic(**member.model_dump())

    # UPDATE
    def update_member(self, memberid: str, data: MemberUpdate) -> MemberPublic:
        log = logger.bind(operation="update_member", memberid=memberid)
        member = self.repo.get(memberid)
        if not member:
            log.error("Member not found for update")
            raise EntityNotFoundError(context={"memberid": memberid})

        member.update_from(data)
        self.repo.update(memberid, member)
        log.info("Member updated successfully")
        return MemberPublic(**member.model_dump())

    # DELETE
    def remove_member(self, data: MemberDelete) -> None:
        log = logger.bind(operation="remove_member", memberid=data.memberid)
        member = self.repo.get(data.memberid)
        if not member:
            log.error("Member not found for deletion")
            raise EntityNotFoundError(context={"memberid": data.memberid})
        self.repo.remove(data.memberid)
        log.info("Member removed successfully")

    # LIST
    def list_members(self) -> list[MemberPublic]:
        log = logger.bind(operation="list_members")
        members = [MemberPublic(**m.model_dump()) for m in self.repo.all()]
        log.info("Listed all members", count=len(members))
        return members
