from app.repositories.base_repo import AbstractRepository
from app.schemas.sch_member import MemberInDB


class InMemoryMemberRepository(AbstractRepository[MemberInDB, str]):
    """Repository in-memory untuk Member."""

    def __init__(self):
        self._data: dict[str, MemberInDB] = {}

    def add(self, key: str, entity: MemberInDB) -> None:
        if key in self._data:
            raise ValueError(f"Member {key} sudah ada.")
        self._data[key] = entity

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
