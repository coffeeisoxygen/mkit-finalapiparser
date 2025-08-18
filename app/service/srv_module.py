"""module service logic."""

from pydantic import SecretStr

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


import asyncio


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
    async def create_module(self, data: ModuleCreate) -> ModulePublic:
        moduleid = await self._next_id()
        log = logger.bind(operation="create_module", moduleid=moduleid)

        # check duplicate
        existing = await self.repo.get(moduleid)
        if existing:
            log.error("Module already exists")
            raise EntityAlreadyExistsError(context={"moduleid": moduleid})

        # Konversi field sensitif ke SecretStr
        module = ModuleInDB(
            moduleid=moduleid,
            provider=data.provider,
            name=data.name,
            base_url=data.base_url,
            username=data.username,
            msisdn=data.msisdn,
            pin=SecretStr(data.pin) if isinstance(data.pin, str) else data.pin,
            password=SecretStr(data.password)
            if isinstance(data.password, str)
            else data.password,
            email=data.email,
            is_active=True,
        )
        await self.repo.add(module.moduleid, module)
        log.info("Module created successfully")
        return ModulePublic(**module.model_dump())

    # READ
    async def get_module(self, moduleid: str) -> ModulePublic | None:
        log = logger.bind(operation="get_module", moduleid=moduleid)
        module = await self.repo.get(moduleid)
        if module:
            log.info("Module retrieved")
            return ModulePublic(**module.model_dump())
        else:
            log.error("Module not found")
            raise EntityNotFoundError(context={"moduleid": moduleid})

    # UPDATE
    async def update_module(self, moduleid: str, data: ModuleUpdate) -> ModulePublic:
        log = logger.bind(operation="update_module", moduleid=moduleid)
        existing = await self.repo.get(moduleid)
        if not existing:
            log.error("Module not found for update")
            raise EntityNotFoundError(context={"moduleid": moduleid})

        # Robustly convert pin/password to SecretStr if needed
        patch = data.model_dump(exclude_unset=True)
        if "pin" in patch and isinstance(patch["pin"], str):
            patch["pin"] = SecretStr(patch["pin"])
        if "password" in patch and isinstance(patch["password"], str):
            patch["password"] = SecretStr(patch["password"])
        for k, v in patch.items():
            setattr(existing, k, v)
        await self.repo.update(moduleid, existing)
        log.info("Module updated successfully")
        return ModulePublic(**existing.model_dump())

    # DELETE
    async def remove_module(self, data: ModuleDelete) -> None:
        log = logger.bind(operation="remove_module", moduleid=data.moduleid)
        module = await self.repo.get(data.moduleid)
        if not module:
            log.error("Module not found for deletion")
            raise EntityNotFoundError(context={"moduleid": data.moduleid})
        await self.repo.remove(data.moduleid)
        log.info("Module removed successfully")

    # LIST
    async def list_modules(self) -> list[ModulePublic]:
        log = logger.bind(operation="list_modules")
        modules = [ModulePublic(**m.model_dump()) for m in await self.repo.all()]
        log.info("Listed all modules", count=len(modules))
        return modules
