from typing import Annotated

from fastapi import Depends, Request

from app.repositories.rep_member import InMemoryMemberRepository
from app.repositories.rep_module import InMemoryModuleRepository
from app.repositories.rep_user import UserRepository
from app.service.srv_member import MemberService
from app.service.srv_module import ModuleService


def get_member_repo(request: Request) -> InMemoryMemberRepository:
    return request.app.state.member_repo


def get_module_repo(request: Request) -> InMemoryModuleRepository:
    return request.app.state.module_repo


def get_user_repo(request: Request) -> UserRepository:
    return request.app.state.auth_repo


def get_member_service(repo=Depends(get_member_repo)):
    return MemberService(repo)


def get_module_service(repo=Depends(get_module_repo)):
    return ModuleService(repo)


# Anotated for easier to use


DepMemberRepo = Annotated[InMemoryMemberRepository, Depends(get_member_repo)]
DepModuleRepo = Annotated[InMemoryModuleRepository, Depends(get_module_repo)]
DepMemberService = Annotated[MemberService, Depends(get_member_service)]
DepModuleService = Annotated[ModuleService, Depends(get_module_service)]
