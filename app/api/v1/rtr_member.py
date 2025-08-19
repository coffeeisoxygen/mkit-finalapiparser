# from fastapi import APIRouter

# from app.custom.exceptions import EntityAlreadyExistsError, EntityNotFoundError
# from app.custom.exceptions.utils import generate_responses
# from app.deps.deps_service import DepMemberService
# from app.schemas.sch_member import (
#     MemberCreate,
#     MemberDelete,
#     MemberPublic,
#     MemberUpdate,
# )

# router = APIRouter(
#     prefix="/api/v1/member",
#     tags=["Member"],
# )


# @router.get(
#     "/{memberid}",
#     response_model=MemberPublic,
#     responses=generate_responses(EntityNotFoundError),
# )
# async def get_member(memberid: str, service: DepMemberService):
#     """Ambil data member berdasarkan ID."""
#     return await service.get(memberid)


# @router.get("/", response_model=list[MemberPublic])
# async def list_members(service: DepMemberService):
#     """Ambil daftar semua member."""
#     return await service.list()


# @router.post(
#     "/",
#     response_model=MemberPublic,
#     responses=generate_responses(EntityAlreadyExistsError),
# )
# async def create_member(data: MemberCreate, service: DepMemberService):
#     """Buat member baru."""
#     return await service.create(data)


# @router.put(
#     "/{memberid}",
#     response_model=MemberPublic,
#     responses=generate_responses(EntityNotFoundError),
# )
# async def update_member(memberid: str, data: MemberUpdate, service: DepMemberService):
#     """Update data member berdasarkan ID."""
#     return await service.update(memberid, data)


# @router.delete(
#     "/{memberid}",
#     status_code=204,
#     responses=generate_responses(EntityNotFoundError),
# )
# async def remove_member(memberid: str, service: DepMemberService):
#     """Hapus member berdasarkan ID."""
#     data = MemberDelete(memberid=memberid)
#     await service.remove(data)
#     return None
