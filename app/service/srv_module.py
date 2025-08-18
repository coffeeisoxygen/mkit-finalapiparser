"""module service logic (refactored)."""

import asyncio

from app.custom.exceptions.cst_exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)
from app.mlogg import logger
from app.repositories.rep_module import AsyncInMemoryModuleRepo
from app.schemas.sch_module import (
    ModuleCreate,
    ModuleDelete,
    ModuleInDB,
    ModulePublic,
    ModuleUpdate,
)

PREFIX_MODULE = "MOD"


class ModuleService:
    """Service layer untuk module (business logic)."""

    def __init__(self, repo: AsyncInMemoryModuleRepo):
        self.repo = repo
        self._counter = 0
        self._lock = asyncio.Lock()

    async def _next_id(self) -> str:
        async with self._lock:
            self._counter += 1
            return f"{PREFIX_MODULE}{str(self._counter).zfill(3)}"

    # CREATE
    async def create(self, data: ModuleCreate) -> ModulePublic:
        moduleid = await self._next_id()
        log = logger.bind(op="create_module", moduleid=moduleid)

        if await self.repo.get(moduleid):
            raise EntityAlreadyExistsError(context={"moduleid": moduleid})

        module = ModuleInDB.from_create(moduleid, data)
        await self.repo.add(moduleid, module)

        log.info("Module created")
        return ModulePublic(**module.model_dump())

    # READ
    async def get(self, moduleid: str) -> ModulePublic:
        log = logger.bind(op="get_module", moduleid=moduleid)
        module = await self.repo.get(moduleid)
        if not module:
            raise EntityNotFoundError(context={"moduleid": moduleid})
        log.info("Module retrieved")
        return ModulePublic(**module.model_dump())

    # UPDATE
    async def update(self, moduleid: str, data: ModuleUpdate) -> ModulePublic:
        log = logger.bind(op="update_module", moduleid=moduleid)
        module = await self.repo.get(moduleid)
        if not module:
            raise EntityNotFoundError(context={"moduleid": moduleid})

        module.update_from(data)
        await self.repo.update(moduleid, module)

        log.info("Module updated")
        return ModulePublic(**module.model_dump())

    # DELETE
    async def remove(self, data: ModuleDelete) -> None:
        log = logger.bind(op="remove_module", moduleid=data.moduleid)
        if not await self.repo.get(data.moduleid):
            raise EntityNotFoundError(context={"moduleid": data.moduleid})
        await self.repo.remove(data.moduleid)
        log.info("Module removed")

    # LIST
    async def list(self) -> list[ModulePublic]:
        modules = [ModulePublic(**m.model_dump()) for m in await self.repo.all()]
        logger.info("Listed modules", count=len(modules))
        return modules
