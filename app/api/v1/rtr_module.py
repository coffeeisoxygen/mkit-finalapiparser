"""Router untuk modul."""

from fastapi import APIRouter

from app.custom.exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)
from app.custom.exceptions.utils import generate_responses
from app.deps.deps_service import DepModuleService
from app.schemas.sch_module import (
    ModuleCreate,
    ModuleDelete,
    ModulePublic,
    ModuleUpdate,
)

router = APIRouter()


# ---------------------------
# POST /module
# ---------------------------
@router.post(
    "/",
    response_model=ModulePublic,
    responses=generate_responses(EntityAlreadyExistsError),
)
def create_module(data: ModuleCreate, service: DepModuleService):
    """Buat modul baru."""
    return service.create_module(data)


# ---------------------------
# GET /module/{moduleid}
# ---------------------------
@router.get(
    "/{moduleid}",
    response_model=ModulePublic,
    responses=generate_responses(EntityNotFoundError),
)
def get_module(moduleid: str, service: DepModuleService):
    """Ambil modul by ID."""
    return service.get_module(moduleid)


# ---------------------------
# PUT /module/{moduleid}
# ---------------------------
@router.put(
    "/{moduleid}",
    response_model=ModulePublic,
    responses=generate_responses(EntityNotFoundError),
)
def update_module(moduleid: str, data: ModuleUpdate, service: DepModuleService):
    """Update data modul."""
    return service.update_module(moduleid, data)


# ---------------------------
# DELETE /module
# ---------------------------
@router.delete(
    "/",
    status_code=204,
    responses=generate_responses(EntityNotFoundError),
)
def remove_module(data: ModuleDelete, service: DepModuleService):
    """Hapus modul."""
    service.remove_module(data)
    return None


# ---------------------------
# GET /module
# ---------------------------
@router.get("/", response_model=list[ModulePublic])
def list_modules(service: DepModuleService):
    """Ambil semua modul."""
    return service.list_modules()
