from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.repositories.lite_repo_user import LiteUserRepo
from app.crud.uow.abstract import AbstractUnitOfWork
from app.mlogg import logger


class AsyncUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session: AsyncSession):
        self.session = session
        self._committed = False
        with logger.contextualize(uow="AsyncUnitOfWork"):
            logger.debug("AsyncUnitOfWork initialized")

    async def __aenter__(self):
        # Initialize repositories dengan session yang sama
        self._init_repositories()
        with logger.contextualize(uow="AsyncUnitOfWork"):
            logger.debug("UoW entered, repositories initialized")
        return self

    def _init_repositories(self):
        """Initialize semua repositories dengan shared session."""
        self.user_repo = LiteUserRepo(self.session)

    async def commit(self):
        if not self._committed:
            await self.session.commit()
            self._committed = True
            with logger.contextualize(uow="AsyncUnitOfWork"):
                logger.info("Transaction committed")

    async def rollback(self):
        await self.session.rollback()
        with logger.contextualize(uow="AsyncUnitOfWork"):
            logger.info("Transaction rolled back")

    async def flush(self):
        """Flush untuk get IDs tanpa commit."""
        await self.session.flush()
        with logger.contextualize(uow="AsyncUnitOfWork"):
            logger.debug("Session flushed")

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ):
        with logger.contextualize(uow="AsyncUnitOfWork"):
            logger.debug(
                "UoW exiting", exc_type=exc_type, has_exception=exc_type is not None
            )

        try:
            if exc_type:
                await self.rollback()
            elif not self._committed:
                await self.commit()
        except Exception as e:
            logger.error(f"Error during UoW exit: {e}")
            if exc_type and exc is not None:
                raise exc from e
            raise e
        finally:
            await self.session.close()
            with logger.contextualize(uow="AsyncUnitOfWork"):
                logger.debug("UoW exited successfully")
