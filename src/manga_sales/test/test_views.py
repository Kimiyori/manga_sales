import pytest
import pytest_asyncio
from src.main import main


@pytest_asyncio.fixture
async def main_app(aiohttp_client):
    client = await aiohttp_client(await main())
    return client


@pytest.mark.asyncio
async def test_source_view(main_app):
    resp=await main_app.get("/")
    assert resp.status == 200

@pytest.mark.asyncio
async def test_source_type_view(main_app):
    resp=await main_app.get("/oricon")
    assert resp.status == 200