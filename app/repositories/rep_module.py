from app.repositories.base_repo import AbstractRepository
from app.schemas.sch_module import ModuleInDB


class InMemoryModuleRepository(AbstractRepository[ModuleInDB, str]):
    """Repository in-memory untuk Module."""

    def __init__(self):
        self._data: dict[str, ModuleInDB] = {}

    def add(self, key: str, entity: ModuleInDB) -> None:
        if key in self._data:
            raise ValueError(f"Module {key} sudah ada.")
        self._data[key] = entity

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
