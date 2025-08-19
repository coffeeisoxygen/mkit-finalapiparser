from sqlalchemy.ext.asyncio import AsyncSession

from app.mlogg import logger
from app.mlogg.utils import logger_wraps


class UnitOfWork:
    """Unit of Work pattern untuk handle transaksi multi-step.

    Digunakan untuk mengelola transaksi database yang melibatkan beberapa operasi.

    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self._committed = False
        self.log = logger.bind(uow=self.__class__.__name__)
        self.log.info("UnitOfWork initialized")

    @logger_wraps(entry=True, exit=True, level="INFO")
    async def commit(self):
        await self.session.commit()
        self._committed = True

    @logger_wraps(entry=True, exit=True, level="INFO")
    async def rollback(self):
        await self.session.rollback()

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object | None,
    ):
        if exc_type:
            await self.rollback()
        elif not self._committed:
            await self.commit()
