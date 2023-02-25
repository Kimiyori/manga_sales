from unittest import mock
import pytest
import pytest_asyncio
from manga_sales.containers import DatabaseContainer
from manga_sales.db.data_access_layers.item import ItemDAO

from manga_sales.db.data_access_layers.source import SourceDAO
from manga_sales.db.data_access_layers.week import WeekDAO
from .conftest import dao_session
from config.main import create_app
from manga_sales.db.data_access_layers.source_type import SourceTypeDAO


@pytest_asyncio.fixture
async def app():
    app = await create_app()
    app.container = DatabaseContainer()
    yield app
    app.container.unwire()


@pytest_asyncio.fixture
async def main_app(aiohttp_client, app):
    client = await aiohttp_client(app)
    return client


@pytest.mark.usefixtures("create_data")
@pytest.mark.parametrize("dao", [SourceDAO])
async def test_source_view(main_app, app, dao_session):
    with app.container.source.override(dao_session):
        resp = await main_app.get("/source")
        assert resp.status == 200
        text = await resp.text()
        assert all(x.name in text for x in pytest.sources)




@pytest.mark.usefixtures("create_data")
@pytest.mark.parametrize("dao", [WeekDAO])
async def test_week_view(main_app, app, dao_session):
    url = f"/source/{pytest.sources[0].name.lower()}/{pytest.source_types[0].type.lower()}"
    with app.container.week.override(dao_session):
        resp = await main_app.get(url)
        assert resp.status == 200
        text = await resp.text()
        assert all(str(x.date.day) in text for x in pytest.weeks)


@pytest.mark.usefixtures("create_data")
@pytest.mark.parametrize("dao", [ItemDAO])
async def test_item_view(main_app, app, dao_session):
    url = f"/source/{pytest.sources[0].name.lower()}/{pytest.source_types[0].type.lower()}/{pytest.weeks[0].date.strftime('%Y-%m-%d')}"
    with app.container.item.override(dao_session):
        resp = await main_app.get(url)
        assert resp.status == 200
        text = await resp.text()
        assert pytest.titles[0].name in text
