
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import text


Base = declarative_base()


class AsyncDatabaseSession:
    def __init__(self, data):
        self._session = None
        self._engine = None
        self.data = data

    def __getattr__(self, name):
        return getattr(self._session, name)

    def init(self,echo=True):
        DSN = f"postgresql+asyncpg://{self.data['user']}:{self.data['password']}@{self.data['host']}:{self.data['port']}/{self.data['database']}"
        self._engine = create_async_engine(
            DSN,
            future=True,
            echo=echo,
        )
        self._session = sessionmaker(
            self._engine, expire_on_commit=False, class_=AsyncSession
        )

    @property
    def get_session(self):
        return self._session

    async def create_all(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def create_db(self):
        async with self._engine.connect() as conn:
            await conn.execution_options(isolation_level="AUTOCOMMIT")
            await conn.execute(text('drop database if exists test'))
            await conn.execute(text('create database test'))

    async def delete_db(self):
        async with self._engine.connect() as conn:
            await conn.execution_options(isolation_level="AUTOCOMMIT")
            await conn.execute(text('drop database if exists test WITH (FORCE)'))
        await self._engine.dispose()