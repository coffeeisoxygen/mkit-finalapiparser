"""Module service layer."""

from app.repositories.memory.rep_module import AsyncInMemoryModuleRepo
from app.schemas.sch_module import (
    ModuleCreate,
    ModuleDelete,
    ModuleInDB,
    ModulePublic,
    ModuleUpdate,
)
from app.service.crud.base_service import BaseService


class ModuleService(
    BaseService[ModuleCreate, ModuleUpdate, ModuleDelete, ModuleInDB, ModulePublic]
):
    def __init__(self, repo: AsyncInMemoryModuleRepo):
        super().__init__(repo, prefix="MOD")

    # mapping abstract methods
    def _to_in_db(self, obj_id: str, data: ModuleCreate) -> ModuleInDB:
        return ModuleInDB.from_create(obj_id, data)

    def _to_public(self, obj: ModuleInDB) -> ModulePublic:
        return ModulePublic(**obj.model_dump())
