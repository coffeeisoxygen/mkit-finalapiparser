# app/repositories/inmemory_repo.py
import asyncio
from typing import TypeVar

from app.custom.exceptions import EntityAlreadyExistsError, EntityNotFoundError
from app.repositories.abs_repo import AsbtractAsyncRepos

T = TypeVar("T")  # entity type
K = TypeVar("K")  # key type


class AsyncInMemoryRepo[T, K](AsbtractAsyncRepos[T, K]):
    """Generic async-safe in-memory repository."""

    def __init__(self):
        self._data: dict[K, T] = {}
        self._lock = asyncio.Lock()

    async def add(self, key: K, entity: T) -> None:
        async with self._lock:
            if key in self._data:
                raise EntityAlreadyExistsError(f"Entity {key} sudah ada.")
            self._data[key] = entity

    async def get(self, key: K) -> T | None:
        async with self._lock:
            return self._data.get(key)

    async def update(self, key: K, entity: T) -> None:
        async with self._lock:
            if key not in self._data:
                raise EntityNotFoundError(f"Entity {key} tidak ditemukan.")
            self._data[key] = entity

    async def remove(self, key: K) -> None:
        async with self._lock:
            if key not in self._data:
                raise EntityNotFoundError(f"Entity {key} tidak ditemukan.")
            self._data.pop(key)

    async def all(self) -> list[T]:
        async with self._lock:
            return list(self._data.values())
