from app.repositories.rep_member import InMemoryMemberRepository
from app.repositories.rep_module import InMemoryModuleRepository
from app.service.srv_member import MemberService
from app.service.srv_module import ModuleService

# Dependency for MemberService


def get_member_service() -> MemberService:
    repo = InMemoryMemberRepository()
    return MemberService(repo)


# Dependency for ModuleService


def get_module_service() -> ModuleService:
    repo = InMemoryModuleRepository()
    return ModuleService(repo)


"""dependencies management for all services."""
