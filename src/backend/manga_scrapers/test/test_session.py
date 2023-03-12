from unittest import mock
import pytest
import pytest_asyncio
from config.config import PROXY_URL
from manga_scrapers.exceptions import ConnectError
from manga_scrapers.exceptions import IncorrectMethod, NotFound, Unsuccessful
from manga_scrapers.client_handler.session_context_manager import Session
from aioresponses import aioresponses
from manga_scrapers.test.conftest import proxy_mock

TEST_URL = "http://example.com"


@pytest_asyncio.fixture
async def client_session():
    async with Session() as session:
        yield session


@pytest.fixture
def aioresponse():
    with aioresponses() as m:
        yield m


async def test_proxy(client_session):
    assert client_session.proxy_list == [None]


async def test_invalid_proxies(aioresponse, client_session):
    with pytest.raises(ConnectError) as context:
        aioresponse.get(TEST_URL, status=503, repeat=True)
        await client_session.fetch(TEST_URL)
        assert "Failed to connect, perhabs due to invalid proxies" == str(
            context.exception
        )


def test_rotate_proxies():
    session = Session()
    proxies_list = ["a", "b", "c"]
    session.proxy_list = proxies_list
    proxy_index = initial_index = session.choose_proxy()
    c = 0
    with pytest.raises(ConnectError):
        while True:
            c+=1
            proxy_index = session.rotate_proxy(proxy_index, initial_index)
    assert c ==3

async def test_200(aioresponse, client_session):
    aioresponse.get(TEST_URL, status=200)
    response = await client_session.fetch(TEST_URL)
    assert response.status == 200


async def test_correct_method_error(aioresponse, client_session):
    corrert_methods = ["content", "read"]
    body_text = "test"
    aioresponse.get(TEST_URL, status=200, body=body_text)
    response = await client_session.fetch(TEST_URL, commands=corrert_methods)
    assert isinstance(response.decode("ascii"), str)
    assert response.decode("ascii") == body_text


async def test_incorrect_method_error(aioresponse, client_session):
    wrong_method = ["something"]
    with pytest.raises(IncorrectMethod) as context:
        aioresponse.get(TEST_URL, status=200)
        await client_session.fetch(TEST_URL, commands=wrong_method)
        assert f"Response object does not have given attribute - {wrong_method}" in str(
            context.exception
        )


async def test_404_error(aioresponse, client_session):
    with pytest.raises(NotFound) as context:
        aioresponse.get(TEST_URL, status=404)
        await client_session.fetch(TEST_URL)
        assert "Can't find given page" in str(context.exception)


async def test_500_error(aioresponse, client_session):
    with pytest.raises(Unsuccessful) as context:
        aioresponse.get(TEST_URL, status=500)
        await client_session.fetch(TEST_URL)
        assert "Status code is 500" in str(context.exception)
