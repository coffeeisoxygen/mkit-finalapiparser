# app/routers/router_member.py

from app.deps.deps_service import DepMemberService
from app.schemas.sch_member import (
    MemberCreate,
    MemberDelete,
    MemberPublic,
    MemberUpdate,
)
from fastapi import APIRouter

router = APIRouter(prefix="/members", tags=["Member"])


@router.post("/", response_model=MemberPublic)
def create_member(data: MemberCreate, service: DepMemberService):
    """Buat member baru."""
    return service.create_member(data)


@router.get("/{memberid}", response_model=MemberPublic)
def get_member(memberid: str, service: DepMemberService):
    """Ambil member by ID."""
    return service.get_member(memberid)


@router.put("/{memberid}", response_model=MemberPublic)
def update_member(memberid: str, data: MemberUpdate, service: DepMemberService):
    """Update data member."""
    return service.update_member(memberid, data)


@router.delete("/", status_code=204)
def remove_member(data: MemberDelete, service: DepMemberService):
    """Hapus member."""
    service.remove_member(data)
    return None


@router.get("/", response_model=list[MemberPublic])
def list_members(service: DepMemberService):
    """Ambil semua member."""
    return service.list_members()
