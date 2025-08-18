"""Dependency injection for repositories and services."""

from typing import Annotated

from fastapi import Depends, Request

from app.repositories import AsyncInMemoryMemberRepo, AsyncInMemoryModuleRepo
from app.repositories.memory.rep_user import UserRepository
from app.service import MemberService, ModuleService

# ───────────────────────────────
# Repository Factories
# ───────────────────────────────


def get_member_repo(request: Request) -> AsyncInMemoryMemberRepo:
    return request.app.state.member_repo


def get_module_repo(request: Request) -> AsyncInMemoryModuleRepo:
    return request.app.state.module_repo


def get_user_repo(request: Request) -> UserRepository:
    return request.app.state.auth_repo


# ───────────────────────────────
# Service Factories
# ───────────────────────────────


def get_member_service(
    repo: AsyncInMemoryMemberRepo = Depends(get_member_repo),
) -> MemberService:
    return MemberService(repo)


def get_module_service(
    repo: AsyncInMemoryModuleRepo = Depends(get_module_repo),
) -> ModuleService:
    return ModuleService(repo)


# ───────────────────────────────
# Annotated Shortcuts (for router)
# ───────────────────────────────

DepMemberRepo = Annotated[AsyncInMemoryMemberRepo, Depends(get_member_repo)]
DepModuleRepo = Annotated[AsyncInMemoryModuleRepo, Depends(get_module_repo)]
DepUserRepo = Annotated[UserRepository, Depends(get_user_repo)]

DepMemberService = Annotated[MemberService, Depends(get_member_service)]
DepModuleService = Annotated[ModuleService, Depends(get_module_service)]
