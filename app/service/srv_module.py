"""module service logic."""

from app.repositories.rep_module import InMemoryModuleRepository
from app.schemas.sch_module import (
    ModuleCreate,
    ModuleDelete,
    ModulePublic,
    ModuleUpdate,
)


class ModuleService:
    """Service untuk mengelola module."""

    """Business logic untuk Member."""

    def __init__(self, repo: InMemoryModuleRepository):
        self.repo = repo

    def register(self, data: ModuleCreate) -> ModulePublic:
        """Register module baru."""
        module = self.repo.create(data)
        return ModulePublic(**module.model_dump())

    def update(self, moduleid: str, data: ModuleUpdate) -> ModulePublic:
        """Update module."""
        module = self.repo.get(moduleid)
        if not module:
            raise KeyError(f"Module {moduleid} tidak ditemukan.")

        update_data = data.model_dump(exclude_unset=True)
        updated = module.model_copy(update=update_data)
        self.repo.update(moduleid, updated)
        return ModulePublic(**updated.model_dump())

    def delete(self, data: ModuleDelete) -> None:
        """Hapus module berdasarkan ID."""
        self.repo.remove(data.moduleid)

    def list_modules(self) -> list[ModulePublic]:
        """Ambil semua module publik."""
        return [ModulePublic(**m.model_dump()) for m in self.repo.all()]
