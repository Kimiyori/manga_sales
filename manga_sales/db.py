
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker


Base = declarative_base()



class AsyncDatabaseSession:
    def __init__(self):
        self._session = None
        self._engine = None

    def __getattr__(self, name):
        return getattr(self._session, name)

    def init(self, app):
        conf = app['config']['postgres']
        DSN = f"postgresql+asyncpg://{conf['user']}:{conf['password']}@{conf['host']}:{conf['port']}/{conf['database']}"
        self._engine = create_async_engine(
            DSN,
            future=True,
            echo=True,
        )
        self._session = sessionmaker(
            self._engine, expire_on_commit=False, class_=AsyncSession
        )()

    async def create_all(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


def init_db(app):
    conf = app['config']['postgres']
    DSN = f"postgresql+asyncpg://{conf['user']}:{conf['password']}@{conf['host']}:{conf['port']}/{conf['database']}"
    engine = create_async_engine(
        DSN,
        future=True,
        echo=True,
    )
    session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    return session

#db = AsyncDatabaseSession()

