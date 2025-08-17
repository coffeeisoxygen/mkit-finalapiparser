"""In-memory repository untuk Member."""

from app.repositories.base_repo import AbstractRepository
from app.schemas.sch_member import MemberCreate, MemberInDB

PREFIX_MEMBER = "MEM"


class InMemoryMemberRepository(AbstractRepository[MemberInDB, str]):
    """Repository in-memory untuk Member."""

    def __init__(self):
        self._data: dict[str, MemberInDB] = {}
        self._counter: int = 0  # buat generate sequence

    def _next_id(self) -> str:
        """Generate memberid baru dengan format MEM###."""
        self._counter += 1
        return f"{PREFIX_MEMBER}{str(self._counter).zfill(3)}"

    def create(self, data: MemberCreate) -> MemberInDB:
        """Generate ID dan simpan member baru dari DTO."""
        member = MemberInDB(memberid=self._next_id(), **data.model_dump())
        self._data[member.memberid] = member
        return member

    def get(self, key: str) -> MemberInDB | None:
        return self._data.get(key)

    def update(self, key: str, entity: MemberInDB) -> None:
        if key not in self._data:
            raise KeyError(f"Member {key} tidak ditemukan.")
        self._data[key] = entity

    def remove(self, key: str) -> None:
        self._data.pop(key, None)

    def all(self) -> list[MemberInDB]:
        return list(self._data.values())
