from bs4 import BeautifulSoup
import pytest
import pytest_asyncio
from src.data_scraping.containers import DataScrapingContaiter
from aioresponses import aioresponses


@pytest.fixture
def oricon_list():
    with open("src/data_scraping/test/test_files/oricon_list_weeks.html", "rb") as fp:
        yield BeautifulSoup(fp.read(), "html.parser")


@pytest.fixture
def oricon_item():
    with open("src/data_scraping/test/test_files/oricon_item.html", "rb") as fp:
        yield BeautifulSoup(fp.read(), "html.parser")


@pytest.fixture
def amazon():
    with open("src/data_scraping/test/test_files/amazon.html", "rb") as fp:
        yield BeautifulSoup(fp.read(), "html.parser")


@pytest.fixture
def shoseki_weekly_list():
    with open("src/data_scraping/test/test_files/shoseki_list_titles.html", "rb") as fp:
        yield BeautifulSoup(fp.read(), "html.parser")


@pytest.fixture
def shoseki_list():
    with open("src/data_scraping/test/test_files/shoseki_list.html", "rb") as fp:
        yield BeautifulSoup(fp.read(), "html.parser")


@pytest.fixture
def shoseki_item():
    with open("src/data_scraping/test/test_files/shoseki_item.html", "rb") as fp:
        yield BeautifulSoup(fp.read(), "html.parser")


@pytest.fixture
def manga_updates_list():
    with open(
        "src/data_scraping/test/test_files/mangaupdates_titles_list.html", "rb"
    ) as fp:
        yield BeautifulSoup(fp.read(), "html.parser")


@pytest.fixture
def manga_updates_title():
    with open("src/data_scraping/test/test_files/mangaupdates_title.html", "rb") as fp:
        yield BeautifulSoup(fp.read(), "html.parser")


@pytest_asyncio.fixture
async def manga_updates_container():
    container = DataScrapingContaiter()
    yield await container.manga_updates()
    await container.shutdown_resources()


@pytest_asyncio.fixture
async def oricon_container():
    container = DataScrapingContaiter()
    yield await container.oricon_scraper()
    await container.shutdown_resources()


@pytest_asyncio.fixture
async def shoseki_container():
    container = DataScrapingContaiter()
    yield await container.shoseki_scraper()
    await container.shutdown_resources()


@pytest.fixture
def aioresponse():
    with aioresponses() as m:
        yield m
