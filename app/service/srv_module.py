"""module service logic."""

from app.custom.exceptions.cst_exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)
from app.mlogg import logger
from app.repositories.rep_module import InMemoryModuleRepository
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

    def __init__(self, repo: InMemoryModuleRepository):
        self.repo = repo
        self._counter = 0

    def _next_id(self) -> str:
        """Generate moduleid baru dengan format MOD###."""
        self._counter += 1
        return f"{PREFIX_MODULE}{str(self._counter).zfill(3)}"

    # CREATE
    def create_module(self, data: ModuleCreate) -> ModulePublic:
        moduleid = self._next_id()
        log = logger.bind(operation="create_module", moduleid=moduleid)

        def _raise_exists():
            log.error("Module already exists")
            raise EntityAlreadyExistsError(context={"moduleid": moduleid})

        try:
            if self.repo.get(moduleid):
                _raise_exists()
            module = ModuleInDB(
                moduleid=moduleid,
                **data.model_dump(),
            )
            self.repo.add(module.moduleid, module)
            log.info("Module created successfully")
            return ModulePublic(**module.model_dump())
        except EntityAlreadyExistsError:
            log.exception("Failed to create module")
            raise

    # READ
    def get_module(self, moduleid: str) -> ModulePublic | None:
        log = logger.bind(operation="get_module", moduleid=moduleid)
        module = self.repo.get(moduleid)
        if module:
            log.info("Module retrieved")
            return ModulePublic(**module.model_dump())
        else:
            log.error("Module not found")
            raise EntityNotFoundError(context={"moduleid": moduleid})

    # UPDATE
    def update_module(self, moduleid: str, data: ModuleUpdate) -> ModulePublic:
        log = logger.bind(operation="update_module", moduleid=moduleid)
        existing = self.repo.get(moduleid)
        if not existing:
            log.error("Module not found for update")
            raise EntityNotFoundError(context={"moduleid": moduleid})

        updated_data = existing.model_dump()
        patch = data.model_dump(exclude_unset=True)
        updated_data.update(patch)

        updated = ModuleInDB(**updated_data)
        self.repo.update(moduleid, updated)
        log.info("Module updated successfully")
        return ModulePublic(**updated.model_dump())

    # DELETE
    def remove_module(self, data: ModuleDelete) -> None:
        log = logger.bind(operation="remove_module", moduleid=data.moduleid)
        module = self.repo.get(data.moduleid)
        if not module:
            log.error("Module not found for deletion")
            raise EntityNotFoundError(context={"moduleid": data.moduleid})
        self.repo.remove(data.moduleid)
        log.info("Module removed successfully")

    # LIST
    def list_modules(self) -> list[ModulePublic]:
        log = logger.bind(operation="list_modules")
        modules = [ModulePublic(**m.model_dump()) for m in self.repo.all()]
        log.info("Listed all modules", count=len(modules))
        return modules
