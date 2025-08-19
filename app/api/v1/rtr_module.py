# """API Router untuk operasi CRUD pada modul.

# Endpoint:
# - GET /api/v1/module/         : Ambil semua modul
# - GET /api/v1/module/{id}     : Ambil modul berdasarkan ID
# - POST /api/v1/module/        : Buat modul baru
# - PUT /api/v1/module/{id}     : Update modul
# - DELETE /api/v1/module/      : Hapus modul
# """

# from fastapi import APIRouter

# from app.custom.exceptions import (
#     EntityAlreadyExistsError,
#     EntityNotFoundError,
# )
# from app.custom.exceptions.utils import generate_responses
# from app.deps.deps_service import DepModuleService
# from app.schemas.sch_module import (
#     ModuleCreate,
#     ModuleDelete,
#     ModulePublic,
#     ModuleUpdate,
# )

# router = APIRouter(
#     prefix="/api/v1/module",
#     tags=["Module"],
# )


# @router.get("/", response_model=list[ModulePublic])
# async def list_modules(service: DepModuleService):
#     """Ambil semua modul.

#     Returns:
#         List[ModulePublic]: Daftar modul yang tersedia.
#     """
#     return await service.list()


# @router.get(
#     "/{moduleid}",
#     response_model=ModulePublic,
#     responses=generate_responses(EntityNotFoundError),
# )
# async def get_module(moduleid: str, service: DepModuleService):
#     """Ambil modul berdasarkan ID."""
#     return await service.get(moduleid)


# @router.post(
#     "/",
#     response_model=ModulePublic,
#     responses=generate_responses(EntityAlreadyExistsError),
# )
# async def create_module(data: ModuleCreate, service: DepModuleService):
#     """Buat modul baru."""
#     return await service.create(data)


# @router.put(
#     "/{moduleid}",
#     response_model=ModulePublic,
#     responses=generate_responses(EntityNotFoundError),
# )
# async def update_module(moduleid: str, data: ModuleUpdate, service: DepModuleService):
#     """Update data modul berdasarkan ID."""
#     return await service.update(moduleid, data)


# @router.delete(
#     "/",
#     status_code=204,
#     responses=generate_responses(EntityNotFoundError),
# )
# async def remove_module(data: ModuleDelete, service: DepModuleService):
#     """Hapus modul."""
#     await service.remove(data)
#     return None
