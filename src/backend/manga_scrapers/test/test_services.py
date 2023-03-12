import datetime
from unittest import mock
import pytest_asyncio
from manga_scrapers.services.db_service import get_date_list
from manga_scrapers.scrapers.rating_scrapers.oricon_scraper import (
    OriconWeeklyScraper,
)
from manga_scrapers.scrapers.rating_scrapers.shoseki_scraper import (
    ShosekiWeeklyScraper,
)
from manga_scrapers.services.db_service import (
    execute_scraper,
    get_date,
    scraper_factory,
)
from manga_scrapers.test.conftest import *
from manga_scrapers.utils.url_handler import update_url
from manga_sales.db.models import Week


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
async def test_get_date(aioresponse, db_session_container, oricon_container):
    scraper = await scraper_factory("oricon_scraper")
    dates = [datetime.date.today() - datetime.timedelta(days=x) for x in range(1, 5)]
    for x in dates[:-1]:
        aioresponse.get(
            update_url(
                scraper.MAIN_URL,
                path=[x.strftime("%Y-%m-%d")],
                trailing_slash=True,
            ),
            status=404,
        )
    aioresponse.get(
        update_url(
            scraper.MAIN_URL,
            path=[dates[-1].strftime("%Y-%m-%d")],
            trailing_slash=True,
        ),
        status=200,
    )
    res = await get_date(scraper)
    assert res == dates[-1]


@pytest.mark.usefixtures("create_data_scraper")
async def test_get_date_none(aioresponse, db_session_container, oricon_container):
    scraper = await scraper_factory("oricon_scraper")
    dates = [datetime.date.today() - datetime.timedelta(days=x) for x in range(1, 9)]
    for x in dates:
        aioresponse.get(
            update_url(
                scraper.MAIN_URL,
                path=[x.strftime("%Y-%m-%d")],
                trailing_slash=True,
            ),
            status=404,
        )
    res = await get_date(scraper)
    assert res == None


@pytest.mark.usefixtures("create_data_scraper")
async def test_get_date_recursive(aioresponse, db_session_container, oricon_container):
    scraper = await scraper_factory("oricon_scraper")
    dates = [datetime.date.today() + datetime.timedelta(days=x) for x in range(1, 10)]
    for x in dates[:5]:
        aioresponse.get(
            update_url(
                scraper.MAIN_URL,
                path=[x.strftime("%Y-%m-%d")],
                trailing_slash=True,
            ),
            status=404,
        )
    aioresponse.get(
        update_url(
            scraper.MAIN_URL,
            path=[dates[5].strftime("%Y-%m-%d")],
            trailing_slash=True,
        ),
        status=200,
    )
    for x in dates[6:-1]:
        aioresponse.get(
            update_url(
                scraper.MAIN_URL,
                path=[x.strftime("%Y-%m-%d")],
                trailing_slash=True,
            ),
            status=404,
        )
    aioresponse.get(
        update_url(
            scraper.MAIN_URL,
            path=[dates[-1].strftime("%Y-%m-%d")],
            trailing_slash=True,
        ),
        status=200,
    )

    week_session = db_session_container.week()
    week = Week(date=dates[5], source_type_id=pytest.source_types[0].id)
    week_session.add(week)
    session = db_session_container.session()
    await session.commit()

    res = await get_date(scraper)
    assert res == dates[-1]


@mock.patch("manga_scrapers.services.db_service.get_date")
async def test_get_date_list(mock, oricon_container):
    date_list = [
        datetime.date.today() + datetime.timedelta(days=x) for x in range(1, 5)
    ][::-1]
    date_list.append(None)
    mock.side_effect = date_list
    scraper = await scraper_factory("oricon_scraper")
    result = await get_date_list(scraper)
    assert result == sorted(date_list[:-1])
