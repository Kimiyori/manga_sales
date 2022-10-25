# pylint: disable=redefined-outer-name
import asyncio
import pytest
import pytest_asyncio
from sqlalchemy import text
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.config import get_postgres_uri, TEST_DATABASE_NAME
from src.db.base import Base


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="module")
async def test_engine():
    engine_aux = create_async_engine(
        get_postgres_uri(database_name=False),
        future=True,
    )
    await create_db(engine_aux)
    engine = create_async_engine(
        get_postgres_uri(test=True),
        future=True,
        echo=False,
    )
    try:
        yield engine
    finally:
        await drop_db(engine_aux)


@pytest_asyncio.fixture(scope="class")
async def class_session_factory(test_engine):
    await create_tables(test_engine)
    try:
        yield sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)
    finally:
        await drop_tables(test_engine)


@pytest_asyncio.fixture
async def session_factory(test_engine):
    yield sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)


@pytest_asyncio.fixture
async def dao_session(session_factory, dao):
    async with session_factory() as session:
        yield dao(session)


async def create_db(engine) -> None:
    async with engine.connect() as conn:
        await conn.execution_options(isolation_level="AUTOCOMMIT")
        try:
            await conn.execute(text(f"create database {TEST_DATABASE_NAME}"))
        except sqlalchemy.exc.ProgrammingError:
            await conn.execute(
                text(f"drop database if exists {TEST_DATABASE_NAME} WITH (FORCE)")
            )
            await conn.execute(text(f"create database {TEST_DATABASE_NAME}"))


async def create_tables(engine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables(engine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def drop_db(engine) -> None:
    async with engine.connect() as conn:
        await conn.execution_options(isolation_level="AUTOCOMMIT")
        await conn.execute(
            text(f"drop database if exists {TEST_DATABASE_NAME} WITH (FORCE)")
        )
        await engine.dispose()
