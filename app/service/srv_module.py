"""module service logic."""

from app.custom.cst_exceptions import EntityExcError
from app.repositories.base_repo import AbstractRepository
from app.schemas.sch_module import ModuleCreate, ModuleInDB, ModuleUpdate


class ModuleService:
    """Service untuk mengelola module."""

    def __init__(self, repository: AbstractRepository[ModuleInDB, str]):
        self.repository = repository

    def register(self, data: ModuleCreate) -> ModuleInDB:
        """Daftarkan module baru."""
        module_db = ModuleInDB(**data.model_dump())
        if self.repository.get(module_db.moduleid):
            raise EntityExcError(f"Module ID {module_db.moduleid} sudah terdaftar.")
        self.repository.add(module_db.moduleid, module_db)
        return self._mask_module(module_db)

    def get(self, moduleid: str) -> ModuleInDB | None:
        """Ambil module by id."""
        m = self.repository.get(moduleid)
        if not m:
            raise EntityExcError(f"Module dengan ID {moduleid} tidak ditemukan.")
        return self._mask_module(m)

    def list_modules(self) -> list[ModuleInDB]:
        """Ambil semua module."""
        return [self._mask_module(m) for m in self.repository.all()]

    def update(self, moduleid: str, data: ModuleUpdate) -> ModuleInDB:
        """Update data module."""
        module = self.repository.get(moduleid)
        if not module:
            raise EntityExcError(f"Module dengan ID {moduleid} tidak ditemukan.")
        updated_data = module.copy(update=data.dict(exclude_unset=True))
        self.repository.update(moduleid, updated_data)
        return self._mask_module(updated_data)

    def remove(self, moduleid: str) -> None:
        """Hapus module."""
        module = self.repository.get(moduleid)
        if not module:
            raise EntityExcError(f"Module dengan ID {moduleid} tidak ditemukan.")
        self.repository.remove(moduleid)

    def _mask_module(self, module: ModuleInDB) -> ModuleInDB:
        # Mask sensitive fields if needed (example: if module has secret_key)
        # If no sensitive fields, just return as is
        # Example:
        # module.secret_key = None
        return module
