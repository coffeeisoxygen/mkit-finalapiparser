import asyncio

from app.custom.exceptions import EntityAlreadyExistsError, EntityNotFoundError
from app.repositories.base_repo import AsyncRepository, SyncRepository
from app.schemas.sch_member import MemberInDB


# ==========================
# SYNC REPO
# ==========================
class SyncInmemoryMemberRepo(SyncRepository[MemberInDB, str]):
    """Sync in-memory repository for Member."""

    def __init__(self):
        self._data: dict[str, MemberInDB] = {}

    def add(self, key: str, entity: MemberInDB) -> None:
        if key in self._data:
            raise EntityAlreadyExistsError(f"Member {key} sudah ada.")
        self._data[key] = entity

    def get(self, key: str) -> MemberInDB | None:
        return self._data.get(key)

    def update(self, key: str, entity: MemberInDB) -> None:
        if key not in self._data:
            raise EntityNotFoundError(f"Member {key} tidak ditemukan.")
        self._data[key] = entity

    def remove(self, key: str) -> None:
        if key not in self._data:
            raise EntityNotFoundError(f"Member {key} tidak ditemukan.")
        self._data.pop(key)

    def all(self) -> list[MemberInDB]:
        return list(self._data.values())


# ==========================
# ASYNC REPO
# ==========================
class AsyncInmemoryMemberRepo(AsyncRepository[MemberInDB, str]):
    """Async-safe in-memory repository for Member."""

    def __init__(self):
        self._data: dict[str, MemberInDB] = {}
        self._lock = asyncio.Lock()

    async def add(self, key: str, entity: MemberInDB) -> None:
        async with self._lock:
            if key in self._data:
                raise EntityAlreadyExistsError(f"Member {key} sudah ada.")
            self._data[key] = entity

    async def get(self, key: str) -> MemberInDB | None:
        async with self._lock:
            return self._data.get(key)

    async def update(self, key: str, entity: MemberInDB) -> None:
        async with self._lock:
            if key not in self._data:
                raise EntityNotFoundError(f"Member {key} tidak ditemukan.")
            self._data[key] = entity

    async def remove(self, key: str) -> None:
        async with self._lock:
            if key not in self._data:
                raise EntityNotFoundError(f"Member {key} tidak ditemukan.")
            self._data.pop(key)

    async def all(self) -> list[MemberInDB]:
        async with self._lock:
            return list(self._data.values())
