from abc import ABC, abstractmethod

from app.models.db_audit import AuditLog


class IAuditLogRepo(ABC):
    @abstractmethod
    async def log(
        self, description: dict | str, detail: dict | None = None
    ) -> AuditLog:
        """Log audit event to database and return the created AuditLog instance."""
        raise NotImplementedError
