from unittest import mock
import pytest
import pytest_asyncio
from manga_scrapers.exceptions import IncorrectMethod, NotFound, Unsuccessful
from manga_scrapers.client_handler.session_context_manager import Session
from aioresponses import aioresponses

TEST_URL = "http://example.com"


@pytest_asyncio.fixture
async def client_session():
    async with Session() as session:
        yield session


@pytest.fixture
def aioresponse():
    with aioresponses() as m:
        yield m


@pytest.mark.asyncio
async def test_200(aioresponse, client_session):
    aioresponse.get(TEST_URL, status=200)
    response = await client_session.fetch(TEST_URL)
    assert response.status == 200


@pytest.mark.asyncio
async def test_correct_method_error(aioresponse, client_session):
    corrert_methods = ["content", "read"]
    body_text = "test"
    aioresponse.get(TEST_URL, status=200, body=body_text)
    response = await client_session.fetch(TEST_URL, commands=corrert_methods)
    assert isinstance(response.decode("ascii"), str)
    assert response.decode("ascii") == body_text


@pytest.mark.asyncio
async def test_incorrect_method_error(aioresponse, client_session):
    wrong_method = ["something"]
    with pytest.raises(IncorrectMethod) as context:
        aioresponse.get(TEST_URL, status=200)
        await client_session.fetch(TEST_URL, commands=wrong_method)
        assert f"Response object does not have given attribute - {wrong_method}" in str(
            context.exception
        )


@pytest.mark.asyncio
@mock.patch("asyncio.sleep", return_value=0.1)
async def test_429_error(mock, aioresponse):
    with pytest.raises(Unsuccessful) as context:
        aioresponse.get(TEST_URL, status=429, repeat=True)
        async with Session(sleep_time=0.1) as session:
            await session.fetch(TEST_URL)

        assert "Get 429 error too often" in str(context.exception)


@pytest.mark.asyncio
async def test_404_error(aioresponse, client_session):
    with pytest.raises(NotFound) as context:
        aioresponse.get(TEST_URL, status=404)
        await client_session.fetch(TEST_URL)
        assert "Can't find given page" in str(context.exception)


@pytest.mark.asyncio
async def test_500_error(aioresponse, client_session):
    with pytest.raises(Unsuccessful) as context:
        aioresponse.get(TEST_URL, status=500)
        await client_session.fetch(TEST_URL)
        assert "Status code is 500" in str(context.exception)


@pytest.mark.asyncio
async def test_without_context(aioresponse):
    with pytest.raises(AssertionError):
        session = Session()
        aioresponse.get(TEST_URL, status=200)
        await session.fetch(TEST_URL)
