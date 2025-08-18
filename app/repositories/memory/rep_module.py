from app.repositories.memory.base_repo import AsyncInMemoryRepo
from app.schemas.sch_module import ModuleInDB


class AsyncInMemoryModuleRepo(AsyncInMemoryRepo[ModuleInDB, str]):
    """Repo async in-memory khusus Module."""

    pass
