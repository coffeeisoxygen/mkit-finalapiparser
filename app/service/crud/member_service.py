"""Member service layer."""

from app.custom.exceptions.cst_exceptions import EntityAlreadyExistsError
from app.repositories.rep_member import AsyncInMemoryMemberRepo
from app.schemas.sch_member import (
    MemberCreate,
    MemberDelete,
    MemberInDB,
    MemberPublic,
    MemberUpdate,
)
from app.service.crud.base_service import BaseService


class MemberService(
    BaseService[MemberCreate, MemberUpdate, MemberDelete, MemberInDB, MemberPublic]
):
    def __init__(self, repo: AsyncInMemoryMemberRepo):
        super().__init__(repo, prefix="MEM")

    async def create(self, data: MemberCreate) -> MemberPublic:
        # cek unik berdasarkan `name`
        for member in await self.repo.all():
            if member.name == data.name:
                raise EntityAlreadyExistsError(
                    f"Member with name '{data.name}' already exists"
                )
        return await super().create(data)

    # mapping abstract methods
    def _to_in_db(self, obj_id: str, data: MemberCreate) -> MemberInDB:
        return MemberInDB.from_create(obj_id, data)

    def _to_public(self, obj: MemberInDB) -> MemberPublic:
        return MemberPublic(**obj.model_dump())
