from fastapi import APIRouter

from app.deps.deps_service import DepMemberService
from app.mlogg import logger
from app.schemas.sch_member import (
    MemberCreate,
    MemberDelete,
    MemberPublic,
    MemberUpdate,
)

router = APIRouter()


@router.get("/{memberid}", response_model=MemberPublic)
def get_member(
    memberid: str,
    service: DepMemberService,
):
    """Ambil member by ID."""
    return service.get_member(memberid)


@router.get("/", response_model=list[MemberPublic])
def list_members(
    service: DepMemberService,
):
    """Ambil semua member."""
    return service.list_members()


@router.post("/", response_model=MemberPublic)
def create_member(
    data: MemberCreate,
    service: DepMemberService,
):
    """Buat member baru."""
    log = logger.bind(
        operation="create_member",
    )
    result = service.create_member(data)
    log.success("Member created successfully", member_id=result.memberid)
    return result


@router.put("/{memberid}", response_model=MemberPublic)
def update_member(
    memberid: str,
    data: MemberUpdate,
    service: DepMemberService,
):
    """Update data member."""
    return service.update_member(memberid, data)


@router.delete("/{memberid}", status_code=204)
def remove_member(
    memberid: str,
    service: DepMemberService,
):
    """Hapus member by ID."""
    service.remove_member(MemberDelete(memberid=memberid))
    return None
