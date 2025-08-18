from app.repositories.base_repo import AsyncInMemoryRepo
from app.schemas.sch_member import MemberInDB


class AsyncInMemoryMemberRepo(AsyncInMemoryRepo[MemberInDB, str]):
    """Repo async in-memory khusus Member."""

    pass
