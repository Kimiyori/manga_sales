from typing import TYPE_CHECKING, TypeAlias
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import text

if TYPE_CHECKING:
    TSession: TypeAlias = sessionmaker[  # pylint: disable=unsubscriptable-object
        AsyncSession
    ]
else:
    # anything that doesn't raise an exception
    TSession: TypeAlias = AsyncSession
Base = declarative_base()


class AsyncDatabaseSession:
    """
    Class for creating engine and session for SQAAlchemy/
    """

    def __init__(self, data: dict[str, str | int]) -> None:
        self.data = data
        self.init()

    def init(self, echo: bool = True) -> None:
        "Main method for creating session"
        dsn = (
            f"postgresql+asyncpg://{self.data['user']}:"
            f"{self.data['password']}@{self.data['host']}:"
            f"{self.data['port']}/{self.data['database']}"
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


class AsyncTestDatabaseSession:
    """
    Class for creating test engine and session for SQAAlchemy
    """

    def __init__(self, data: dict[str, str | int]) -> None:
        self.data = data
        self.dsn = (
            f"postgresql+asyncpg://{self.data['user']}:"
            f"{self.data['password']}@{self.data['host']}:"
            f"{self.data['port']}"
        )
        self._main_engine: AsyncEngine = create_async_engine(
            self.dsn,
            future=True,
            echo=False,
        )

    async def init(self) -> None:
        "Main method for creating session"
        await self.create_db()
        new_dsn = self.dsn + f"/{self.data['database']}"
        self._test_engine: AsyncEngine = create_async_engine(
            new_dsn,
            future=True,
            echo=False,
        )
        self._session: TSession = sessionmaker(
            self._test_engine, expire_on_commit=False, class_=AsyncSession
        )
        await self.create_all()

    @property
    def get_session(self) -> TSession:
        "Get callable session"
        return self._session

    async def create_all(self) -> None:
        async with self._test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def create_db(self) -> None:
        async with self._main_engine.connect() as conn:
            await conn.execution_options(isolation_level="AUTOCOMMIT")
            try:
                await conn.execute(text(f"create database {self.data['database']}"))
            except sqlalchemy.exc.ProgrammingError:
                await conn.execute(
                    text(
                        f"drop database if exists {self.data['database']} WITH (FORCE)"
                    )
                )
                await conn.execute(text(f"create database {self.data['database']}"))

    async def delete_db(self) -> None:
        async with self._main_engine.connect() as conn:
            await conn.execution_options(isolation_level="AUTOCOMMIT")
            await conn.execute(
                text(f"drop database if exists {self.data['database']} WITH (FORCE)")
            )
        await self._main_engine.dispose()
        await self._test_engine.dispose()
