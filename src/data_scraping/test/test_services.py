import datetime
import functools
from unittest import mock
import pytest_asyncio
from src.data_scraping.containers import DBSessionContainer, DataScrapingContainer
from src.data_scraping.dataclasses import Content
from src.data_scraping.main_scrapers.oricon_scraper import OriconWeeklyScraper
from src.data_scraping.main_scrapers.shoseki_scraper import ShosekiWeeklyScraper
from src.data_scraping.services.db_service import (
    execute_scraper,
    get_date,
    scraper_factory,
)
from src.data_scraping.test.conftest import *
from src.manga_sales.db.models import Week


@pytest_asyncio.fixture
async def containers():
    scrap_cont = DataScrapingContainer()
    yield
    await scrap_cont.shutdown_resources()


async def test_scraper_factory(containers):
    res = await scraper_factory("oricon_scraper")
    assert isinstance(res, OriconWeeklyScraper)
    res2 = await scraper_factory("shoseki_scraper")
    assert isinstance(res2, ShosekiWeeklyScraper)


@pytest.mark.usefixtures("create_data_scraper")
async def test_get_date(aioresponse, db_session_container, containers):
    scraper = await scraper_factory("oricon_scraper")
    dates = [datetime.date.today() - datetime.timedelta(days=x) for x in range(1, 5)]
    for x in dates[:-1]:
        aioresponse.get(scraper.MAIN_URL + x.strftime("%Y-%m-%d") + "/", status=404)
    aioresponse.get(scraper.MAIN_URL + dates[-1].strftime("%Y-%m-%d") + "/", status=200)
    res = await get_date(scraper)
    assert res == dates[-1]


@pytest.mark.usefixtures("create_data_scraper")
async def test_get_date_none(aioresponse, db_session_container, containers):
    scraper = await scraper_factory("oricon_scraper")
    dates = [datetime.date.today() - datetime.timedelta(days=x) for x in range(1, 9)]
    for x in dates:
        aioresponse.get(scraper.MAIN_URL + x.strftime("%Y-%m-%d") + "/", status=404)
    res = await get_date(scraper)
    assert res == None


@pytest.mark.usefixtures("create_data_scraper")
async def test_get_date_recursive(aioresponse, db_session_container, containers):
    scraper = await scraper_factory("oricon_scraper")
    dates = [datetime.date.today() + datetime.timedelta(days=x) for x in range(1, 10)]
    for x in dates[:5]:
        aioresponse.get(scraper.MAIN_URL + x.strftime("%Y-%m-%d") + "/", status=404)
    aioresponse.get(scraper.MAIN_URL + dates[5].strftime("%Y-%m-%d") + "/", status=200)
    for x in dates[6:-1]:
        aioresponse.get(scraper.MAIN_URL + x.strftime("%Y-%m-%d") + "/", status=404)
    aioresponse.get(scraper.MAIN_URL + dates[-1].strftime("%Y-%m-%d") + "/", status=200)

    week_session = db_session_container.week()
    week = Week(date=dates[5], source_type_id=pytest.source_types[0].id)
    week_session.add(week)
    session = db_session_container.session()
    await session.commit()

    res = await get_date(scraper)
    assert res == dates[-1]


@mock.patch(
    "src.data_scraping.services.db_service.return_db_cont",
)
@mock.patch(
    "src.data_scraping.main_scrapers.oricon_scraper.OriconWeeklyScraper.get_data"
)
@pytest.mark.usefixtures("create_data_scraper")
async def test_get_date_full(
    mock, mock_db, aioresponse, db_session_container, containers, faker
):
    contents = []
    for x in range(1, 61):
        contents.append(
            Content(
                name=faker.pystr(max_chars=40),
                volume=faker.pyint(),
                image=faker.pystr(max_chars=40, suffix=".jpg"),
                authors=[faker.name() for _ in range(3)],
                publishers=[faker.name() for _ in range(3)],
                rating=x,
                release_date=faker.date_this_century(),
                sales=faker.pyint(min_value=1_000, max_value=200_000),
            )
        )
    mock.side_effect = [contents[:30], contents[30:]]
    mock_db.return_value = db_session_container
    scraper = await scraper_factory("oricon_scraper")
    dates = [datetime.date.today() - datetime.timedelta(days=x) for x in range(1, 22)]
    for x in dates[:6]:
        aioresponse.get(scraper.MAIN_URL + x.strftime("%Y-%m-%d") + "/", status=404)
    aioresponse.get(scraper.MAIN_URL + dates[6].strftime("%Y-%m-%d") + "/", status=200)
    for x in dates[7:13]:
        aioresponse.get(scraper.MAIN_URL + x.strftime("%Y-%m-%d") + "/", status=404)
    aioresponse.get(scraper.MAIN_URL + dates[13].strftime("%Y-%m-%d") + "/", status=200)
    for x in dates[14:]:
        aioresponse.get(scraper.MAIN_URL + x.strftime("%Y-%m-%d") + "/", status=404)
    await execute_scraper("oricon_scraper")
    items = db_session_container.item()
    res = await items.get_instance(dates[6].strftime("%Y-%m-%d"))
    assert len(res) == 30
    res2 = await items.get_instance(dates[13].strftime("%Y-%m-%d"))
    assert len(res2) == 30
    count_res = await items.get_count()
    assert count_res == 60
