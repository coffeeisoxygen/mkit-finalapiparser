"""A generic repository interface."""

from abc import ABC, abstractmethod
from typing import TypeVar

T = TypeVar("T")  # entity type
K = TypeVar("K")  # key type


class AbstractRepository[T, K](ABC):
    """Interface repository generic."""

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
