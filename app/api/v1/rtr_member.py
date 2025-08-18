from fastapi import APIRouter

from app.custom.exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)
from app.custom.exceptions.utils import generate_responses
from app.deps.deps_service import DepMemberService
from app.schemas.sch_member import (
    MemberCreate,
    MemberDelete,
    MemberPublic,
    MemberUpdate,
)

router = APIRouter()


# ---------------------------
# GET /member/{memberid}
# ---------------------------
@router.get(
    "/{memberid}",
    response_model=MemberPublic,
    responses=generate_responses(EntityNotFoundError),
)
def get_member(memberid: str, service: DepMemberService):
    """Ambil member by ID."""
    return service.get_member(memberid)


# ---------------------------
# GET /member
# ---------------------------
@router.get("/", response_model=list[MemberPublic])
def list_members(service: DepMemberService):
    """Ambil semua member."""
    return service.list_members()


# ---------------------------
# POST /member
# ---------------------------
@router.post(
    "/",
    response_model=MemberPublic,
    responses=generate_responses(EntityAlreadyExistsError),
)
def create_member(data: MemberCreate, service: DepMemberService):
    """Buat member baru."""
    return service.create_member(data)


# ---------------------------
# PUT /member/{memberid}
# ---------------------------
@router.put(
    "/{memberid}",
    response_model=MemberPublic,
    responses=generate_responses(EntityNotFoundError),
)
def update_member(memberid: str, data: MemberUpdate, service: DepMemberService):
    """Update data member."""
    return service.update_member(memberid, data)


# ---------------------------
# DELETE /member/{memberid}
# ---------------------------
@router.delete(
    "/{memberid}",
    status_code=204,
    responses=generate_responses(EntityNotFoundError),
)
def remove_member(memberid: str, service: DepMemberService):
    """Hapus member by ID."""
    service.remove_member(MemberDelete(memberid=memberid))
    return None
