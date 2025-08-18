"""A generic repository interface."""

from abc import ABC, abstractmethod


class AsbtractAsyncRepos[T, K](ABC):
    """Interface repository generic async."""

    @abstractmethod
    async def add(self, key: K, entity: T) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def get(self, key: K) -> T | None:
        raise NotImplementedError()

    @abstractmethod
    async def update(self, key: K, entity: T) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def remove(self, key: K) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def all(self) -> list[T]:
        raise NotImplementedError()
