"""Interface untuk repository AuditMixin.

Kontrak ini digunakan untuk operasi audit dan soft delete pada entity yang menggunakan AuditMixin.
"""

import uuid
from abc import ABC, abstractmethod
from typing import TypeVar

T = TypeVar("T")  # Entity type


class IAuditMixinRepo[T](ABC):
    """Interface repository untuk operasi audit dan soft delete."""

    @abstractmethod
    async def soft_delete(
        self, entity_id: uuid.UUID | str, actor_id: uuid.UUID | str
    ) -> None:
        """Mark record as soft deleted by actor_id.

        Accepts UUID or string UUID for compatibility with DB drivers.
        """
        pass

    @abstractmethod
    async def restore(self, entity_id: uuid.UUID | str) -> None:
        """Restore soft deleted record.

        Accepts UUID or string UUID for compatibility with DB drivers.
        """
        pass

    @abstractmethod
    async def get_audit_log(self, entity_id: uuid.UUID | str) -> dict:
        """Get audit log/history for entity as dict of audit fields.

        Accepts UUID or string UUID for compatibility with DB drivers.
        """
        pass
