"""A generic repository interface."""

from abc import ABC, abstractmethod


class SyncRepository[T, K](ABC):
    """Interface repository generic sync."""

    @abstractmethod
    def add(self, key: K, entity: T) -> None: ...

    @abstractmethod
    def get(self, key: K) -> T | None: ...

    @abstractmethod
    def update(self, key: K, entity: T) -> None: ...

    @abstractmethod
    def remove(self, key: K) -> None: ...

    @abstractmethod
    def all(self) -> list[T]: ...


class AsyncRepository[T, K](ABC):
    """Interface repository generic async."""

    @abstractmethod
    async def add(self, key: K, entity: T) -> None: ...

    @abstractmethod
    async def get(self, key: K) -> T | None: ...

    @abstractmethod
    async def update(self, key: K, entity: T) -> None: ...

    @abstractmethod
    async def remove(self, key: K) -> None: ...

    @abstractmethod
    async def all(self) -> list[T]: ...
