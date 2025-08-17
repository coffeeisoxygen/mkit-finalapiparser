"""In-memory repository untuk Module."""

from app.repositories.base_repo import AbstractRepository
from app.schemas.sch_module import ModuleCreate, ModuleInDB

PREFIX_MODULE = "MOD"


class InMemoryModuleRepository(AbstractRepository[ModuleInDB, str]):
    """Repository in-memory untuk Module."""

    def __init__(self):
        self._data: dict[str, ModuleInDB] = {}
        self._counter: int = 0  # buat generate sequence

    def _next_id(self) -> str:
        """Generate moduleid baru dengan format MOD###."""
        self._counter += 1
        return f"{PREFIX_MODULE}{str(self._counter).zfill(3)}"

    def create(self, data: ModuleCreate) -> ModuleInDB:
        """Generate ID dan simpan module baru dari DTO."""
        module = ModuleInDB(moduleid=self._next_id(), **data.model_dump())
        self._data[module.moduleid] = module
        return module

    def get(self, key: str) -> ModuleInDB | None:
        return self._data.get(key)

    def update(self, key: str, entity: ModuleInDB) -> None:
        if key not in self._data:
            raise KeyError(f"Module {key} tidak ditemukan.")
        self._data[key] = entity

    def remove(self, key: str) -> None:
        self._data.pop(key, None)

    def all(self) -> list[ModuleInDB]:
        return list(self._data.values())
