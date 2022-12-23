from bs4 import BeautifulSoup
import pytest
import pytest_asyncio
import sqlalchemy
from src.manga_scrapers.containers.title_data_container import AuxScrapingContainer
from src.manga_scrapers.containers.image_container import ImageScrapingContainer
from src.manga_scrapers.containers.rating_container import DataScrapingContainer
from src.manga_sales.containers import DatabaseContainer
from aioresponses import aioresponses
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.config import get_postgres_uri, TEST_DATABASE_NAME
from src.db.base import Base
from src.manga_sales.db.models import (
    Source,
    SourceType,
)


@pytest.fixture
def oricon_list():
    with open(
        "src/manga_scrapers/test/test_files/oricon/oricon_list_weeks.html", "rb"
    ) as fp:
        yield BeautifulSoup(fp.read(), "html.parser")


@pytest.fixture
def amazon_list():
    with open("src/manga_scrapers/test/test_files/amazon/amazon_list.html", "rb") as fp:
        yield BeautifulSoup(fp.read(), "html.parser")


@pytest.fixture
def amazon_item():
    with open("src/manga_scrapers/test/test_files/amazon/amazon_item.html", "rb") as fp:
        yield BeautifulSoup(fp.read(), "html.parser")


@pytest.fixture
def oricon_item():
    with open("src/manga_scrapers/test/test_files/oricon/oricon_item.html", "rb") as fp:
        yield BeautifulSoup(fp.read(), "html.parser")


@pytest.fixture
def amazon():
    with open("src/manga_scrapers/test/test_files/amazon/amazon.html", "rb") as fp:
        yield BeautifulSoup(fp.read(), "html.parser")


@pytest.fixture
def shoseki_weekly_list():
    with open(
        "src/manga_scrapers/test/test_files/shoseki/shoseki_list_titles.html", "rb"
    ) as fp:
        yield BeautifulSoup(fp.read(), "html.parser")


@pytest.fixture
def shoseki_list():
    with open(
        "src/manga_scrapers/test/test_files/shoseki/shoseki_list.html", "rb"
    ) as fp:
        yield BeautifulSoup(fp.read(), "html.parser")


@pytest.fixture
def shoseki_item():
    with open(
        "src/manga_scrapers/test/test_files/shoseki/shoseki_item.html", "rb"
    ) as fp:
        yield BeautifulSoup(fp.read(), "html.parser")


@pytest.fixture
def manga_updates_list():
    with open(
        "src/manga_scrapers/test/test_files/mangaupdates/mangaupdates_titles_list.html",
        "rb",
    ) as fp:
        yield BeautifulSoup(fp.read(), "html.parser")


@pytest.fixture
def manga_updates_title():
    with open(
        "src/manga_scrapers/test/test_files/mangaupdates/mangaupdates_title.html", "rb"
    ) as fp:
        yield BeautifulSoup(fp.read(), "html.parser")


@pytest.fixture
def cdjapan_list():
    with open(
        "src/manga_scrapers/test/test_files/cdjapan/cdjapan_list.html", "rb"
    ) as fp:
        yield BeautifulSoup(fp.read(), "html.parser")


@pytest.fixture
def cdjapan_item():
    with open(
        "src/manga_scrapers/test/test_files/cdjapan/cdjapan_item.html", "rb"
    ) as fp:
        yield BeautifulSoup(fp.read(), "html.parser")


@pytest_asyncio.fixture
async def manga_updates_container():
    container = AuxScrapingContainer()
    yield await container.manga_updates_scraper()
    await container.shutdown_resources()


@pytest_asyncio.fixture
async def amazon_container():
    container = AuxScrapingContainer()
    yield await container.amazon_scraper()
    await container.shutdown_resources()


@pytest_asyncio.fixture
async def cdjapan_container():
    container = ImageScrapingContainer()
    yield await container.cdjapan_scraper()
    await container.shutdown_resources()


@pytest_asyncio.fixture
async def oricon_container():
    container = DataScrapingContainer()
    yield await container.oricon_scraper()
    await container.shutdown_resources()


@pytest_asyncio.fixture
async def shoseki_container():
    container = DataScrapingContainer()
    yield await container.shoseki_scraper()
    await container.shutdown_resources()


@pytest.fixture
def aioresponse():
    with aioresponses() as m:
        yield m


@pytest_asyncio.fixture
async def session(
    session_factory,
):
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def session_factory(test_engine):
    yield sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)


@pytest_asyncio.fixture
async def db_session_container(session):
    container = DatabaseContainer()
    container.session.override(session)
    yield container
    container.unwire()


@pytest_asyncio.fixture
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


@pytest_asyncio.fixture
async def class_session_factory(test_engine):
    await create_tables(test_engine)
    try:
        yield sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)
    finally:
        await drop_tables(test_engine)


async def create_tables(engine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables(engine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


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


async def drop_db(engine) -> None:
    async with engine.connect() as conn:
        await conn.execution_options(isolation_level="AUTOCOMMIT")
        await conn.execute(
            text(f"drop database if exists {TEST_DATABASE_NAME} WITH (FORCE)")
        )
        await engine.dispose()


@pytest_asyncio.fixture
async def create_data_scraper(class_session_factory) -> None:
    async with class_session_factory() as session:
        pytest.sources = [Source(name="Oricon"), Source(name="Shoseki")]
        pytest.source_types = [
            SourceType(type="Weekly"),
            SourceType(type="Weekly"),
        ]
        for x in range(2):
            pytest.source_types[x].source = pytest.sources[x]

        session.add_all(pytest.sources)
        session.add_all(pytest.source_types)
        await session.commit()
