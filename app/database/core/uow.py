from sqlalchemy.ext.asyncio import AsyncSession


class UnitOfWork:
    """Unit of Work pattern untuk handle transaksi multi-step.

    Digunakan untuk mengelola transaksi database yang melibatkan beberapa operasi.

    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self._committed = False

    async def commit(self):
        await self.session.commit()
        self._committed = True

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
