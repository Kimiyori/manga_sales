# pylint: disable=redefined-outer-name
import asyncio
import datetime
import pytest
import pytest_asyncio
from sqlalchemy import text
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from config.config import get_postgres_uri, TEST_DATABASE_NAME
from db.base import Base
from manga_sales.db.models import (
    Author,
    Item,
    Publisher,
    Source,
    SourceType,
    Title,
    Week,
)


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


@pytest_asyncio.fixture(scope="module")
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
        yield dao(session) if dao else session


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


@pytest_asyncio.fixture(scope="module")
async def create_data(class_session_factory) -> None:
    async with class_session_factory() as session:
        pytest.sources = [Source(name="Oricon_test"), Source(name="Shoseki_test")]
        pytest.source_types = [
            SourceType(type="Weekly_test"),
            SourceType(type="Weekly_test"),
        ]
        for x in range(2):
            pytest.source_types[x].source = pytest.sources[x]
        pytest.weeks = [
            Week(date=datetime.date(2022, 9, 11)),
            Week(date=datetime.date(2021, 8, 22)),
        ]
        for x in pytest.weeks:
            x.source_type = pytest.source_types[0]
        pytest.authors = [
            Author(name="test_author"),
            Author(name="test_author2"),
        ]
        pytest.publishers = [
            Publisher(name="test_publisher"),
            Publisher(name="test_publisher2"),
        ]
        pytest.titles = [Title(name="test_title"), Title(name="test_title2")]
        pytest.items = [
            Item(
                rating=1,
                volume=22,
                release_date=datetime.date(2022, 8, 11),
                sold=11.434,
                image="2022-08-11/test.jpg",
            ),
            Item(
                rating=2,
                volume=13,
                release_date=datetime.date(2022, 8, 25),
                sold=5.234,
                image="2022-08-11/test2.jpg",
            ),
        ]
        for i, item in enumerate(pytest.items):
            item.title = pytest.titles[0]
            item.author.append(pytest.authors[i])
            item.publisher.append(pytest.publishers[i])
        for i, week in enumerate(pytest.weeks):
            week.items.append(pytest.items[i])
        session.add_all(pytest.sources)
        session.add_all(pytest.source_types)
        session.add_all(pytest.weeks)
        session.add_all(pytest.authors)
        session.add_all(pytest.publishers)
        session.add_all(pytest.titles)
        session.add_all(pytest.items)
        await session.commit()
