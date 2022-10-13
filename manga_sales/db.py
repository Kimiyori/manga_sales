from typing import TYPE_CHECKING, TypeAlias
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import text

if TYPE_CHECKING:
    TSession: TypeAlias = sessionmaker[AsyncSession]  # pylint: disable=unsubscriptable-object
else:
    # anything that doesn't raise an exception
    TSession: TypeAlias = AsyncSession
Base = declarative_base()


class AsyncDatabaseSession:
    """
    Class for creating engine and session for SQAAlchemy/
    Also creates test session for test cases
    """

    def __init__(self, data: dict[str, str | int]) -> None:
        self.data = data
        self.init()

    def init(self, echo: bool = True) -> None:
        "Main method for creating session"
        dsn = (
            f"postgresql+asyncpg://{self.data['user']}:"
            f"{self.data['password']}@{self.data['host']}:"
            f"{self.data['port']}/{ self.data['database']}"
        )
        self._engine: AsyncEngine = create_async_engine(
            dsn,
            future=True,
            echo=echo,
        )
        self._session: TSession = sessionmaker(
            self._engine, expire_on_commit=False, class_=AsyncSession
        )

    @property
    def get_session(self) -> TSession:
        "Get callable session"
        return self._session

    async def create_all(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def create_db(self) -> None:
        async with self._engine.connect() as conn:
            await conn.execution_options(isolation_level="AUTOCOMMIT")
            await conn.execute(text("drop database if exists test"))
            await conn.execute(text("create database test"))

    async def delete_db(self) -> None:
        async with self._engine.connect() as conn:
            await conn.execution_options(isolation_level="AUTOCOMMIT")
            row = text("drop database if exists test WITH (FORCE)")
            await conn.execute(row)
        await self._engine.dispose()
