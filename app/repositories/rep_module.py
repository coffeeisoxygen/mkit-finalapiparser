import asyncio

from app.custom.exceptions import EntityAlreadyExistsError, EntityNotFoundError
from app.repositories.base_repo import AsyncRepository, SyncRepository
from app.schemas.sch_module import ModuleInDB


# ==========================
# SYNC REPO
# ==========================
class SyncInmemoryModuleRepo(SyncRepository[ModuleInDB, str]):
    """Sync in-memory repository for Module."""

    def __init__(self):
        self._data: dict[str, ModuleInDB] = {}

    def add(self, key: str, entity: ModuleInDB) -> None:
        if key in self._data:
            raise EntityAlreadyExistsError(f"Module {key} sudah ada.")
        self._data[key] = entity

    def get(self, key: str) -> ModuleInDB | None:
        return self._data.get(key)

    def update(self, key: str, entity: ModuleInDB) -> None:
        if key not in self._data:
            raise EntityNotFoundError(f"Module {key} tidak ditemukan.")
        self._data[key] = entity

    def remove(self, key: str) -> None:
        if key not in self._data:
            raise EntityNotFoundError(f"Module {key} tidak ditemukan.")
        self._data.pop(key)

    def all(self) -> list[ModuleInDB]:
        return list(self._data.values())


# ==========================
# ASYNC REPO
# ==========================


class AsyncInmemoryModuleRepo(AsyncRepository[ModuleInDB, str]):
    """Async-safe in-memory repository for Module."""

    def __init__(self):
        self._data: dict[str, ModuleInDB] = {}
        self._lock = asyncio.Lock()

    async def add(self, key: str, entity: ModuleInDB) -> None:
        async with self._lock:
            if key in self._data:
                raise EntityAlreadyExistsError(f"Module {key} sudah ada.")
            self._data[key] = entity

    async def get(self, key: str) -> ModuleInDB | None:
        async with self._lock:
            return self._data.get(key)

    async def update(self, key: str, entity: ModuleInDB) -> None:
        async with self._lock:
            if key not in self._data:
                raise EntityNotFoundError(f"Module {key} tidak ditemukan.")
            self._data[key] = entity

    async def remove(self, key: str) -> None:
        async with self._lock:
            if key not in self._data:
                raise EntityNotFoundError(f"Module {key} tidak ditemukan.")
            self._data.pop(key)

    async def all(self) -> list[ModuleInDB]:
        async with self._lock:
            return list(self._data.values())
