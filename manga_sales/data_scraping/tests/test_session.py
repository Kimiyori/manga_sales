import unittest
import unittest.mock as mock
from aiohttp import web
from ..session_context_manager import Session
from aiohttp.test_utils import AioHTTPTestCase



class MyAppTestCase(unittest.IsolatedAsyncioTestCase):

 
    async def test_example(self,mock_get):
     
        async with Session() as resp:
            s=await resp.fetch('https://realpython.com/testing-third-party-apis-with-mocks/',expect_bs=False)
            self.assertEqual(s.status, 404)
