import unittest
from manga_sales.data_scraping.exceptions import IncorrectMethod, NotFound, Unsuccessful
from manga_sales.data_scraping.session_context_manager import Session
from aioresponses import aioresponses

TEST_URL = "http://example.com"


class TestSession(unittest.IsolatedAsyncioTestCase):
    @aioresponses()
    async def test_200(self, mocked):
        async with Session() as session:
            mocked.get(TEST_URL, status=200)
            response = await session.fetch(TEST_URL)

        self.assertTrue(response.status, 200)

    @aioresponses()
    async def test_correct_method_error(self, mocked):
        corrert_methods = ["content", "read"]
        body_text = "test"
        async with Session() as session:
            mocked.get(TEST_URL, status=200, body=body_text)
            response = await session.fetch(TEST_URL, commands=corrert_methods)
            self.assertIsInstance(response.decode("ascii"), str)
            self.assertEqual(response.decode("ascii"), body_text)

    @aioresponses()
    async def test_incorrect_method_error(self, mocked):
        wrong_method = ["something"]
        async with Session() as session:
            with self.assertRaises(IncorrectMethod) as context:
                mocked.get(TEST_URL, status=200)
                await session.fetch(TEST_URL, commands=wrong_method)
                self.assertTrue(
                    f"Response object does not have given attribute - {wrong_method}"
                    in str(context.exception)
                )

    @aioresponses()
    async def test_429_error(self, mocked):
        with self.assertRaises(Unsuccessful) as context:
            async with Session(1) as session:
                mocked.get(TEST_URL, status=429, body="test", repeat=True)
                await session.fetch(TEST_URL)

            self.assertTrue("Get 429 error too often" in str(context.exception))

    @aioresponses()
    async def test_404_error(self, mocked):
        with self.assertRaises(NotFound) as context:
            async with Session() as session:
                mocked.get(TEST_URL, status=404)
                await session.fetch(TEST_URL)

            self.assertTrue("Can't find given page" in str(context.exception))

    @aioresponses()
    async def test_500_error(self, mocked):
        with self.assertRaises(Unsuccessful) as context:
            async with Session() as session:
                mocked.get(TEST_URL, status=500)
                await session.fetch(TEST_URL)

            self.assertTrue("Status code is 500" in str(context.exception))

    @aioresponses()
    async def test_without_context(self, mocked):
        with self.assertRaises(Unsuccessful) as context:
            session = Session()
            mocked.get(TEST_URL, status=200)
            await session.fetch(TEST_URL)
        self.assertTrue("Use this object as context manager" in str(context.exception))
