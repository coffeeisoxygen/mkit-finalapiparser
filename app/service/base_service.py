"""Abstract Base Service (generic async CRUD)."""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, TypeVar

from app.custom.exceptions.cst_exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)

TCreate = TypeVar("TCreate")
TUpdate = TypeVar("TUpdate")
TDelete = TypeVar("TDelete")
TInDB = TypeVar("TInDB")
TPublic = TypeVar("TPublic")


class BaseService[TCreate, TUpdate, TDelete, TInDB, TPublic](ABC):
    def __init__(self, repo: Any, prefix: str):
        self.repo = repo
        self.prefix = prefix
        self._counter = 0
        self._lock = asyncio.Lock()

    async def _next_id(self) -> str:
        async with self._lock:
            self._counter += 1
            return f"{self.prefix}{str(self._counter).zfill(3)}"

    # CREATE
    async def create(self, data: TCreate) -> TPublic:
        obj_id = await self._next_id()
        if await self.repo.get(obj_id):
            raise EntityAlreadyExistsError(context={f"{self.prefix.lower()}id": obj_id})

        obj = self._to_in_db(obj_id, data)
        await self.repo.add(obj_id, obj)
        return self._to_public(obj)

    # READ
    async def get(self, obj_id: str) -> TPublic:
        obj = await self.repo.get(obj_id)
        if not obj:
            raise EntityNotFoundError(context={f"{self.prefix.lower()}id": obj_id})
        return self._to_public(obj)

    # UPDATE
    async def update(self, obj_id: str, data: TUpdate) -> TPublic:
        obj = await self.repo.get(obj_id)
        if not obj:
            raise EntityNotFoundError(context={f"{self.prefix.lower()}id": obj_id})
        obj.update_from(data)
        await self.repo.update(obj_id, obj)
        return self._to_public(obj)

    # DELETE
    async def remove(self, data: TDelete) -> None:
        obj = await self.repo.get(data.__dict__[f"{self.prefix.lower()}id"])
        if not obj:
            raise EntityNotFoundError(
                context={
                    f"{self.prefix.lower()}id": data.__dict__[
                        f"{self.prefix.lower()}id"
                    ]
                }
            )
        await self.repo.remove(data.__dict__[f"{self.prefix.lower()}id"])

    # LIST
    async def list(self) -> list[TPublic]:
        objs = await self.repo.all()
        return [self._to_public(o) for o in objs]

    # ABSTRACT HOOKS
    @abstractmethod
    def _to_in_db(self, obj_id: str, data: TCreate) -> TInDB: ...

    @abstractmethod
    def _to_public(self, obj: TInDB) -> TPublic: ...
