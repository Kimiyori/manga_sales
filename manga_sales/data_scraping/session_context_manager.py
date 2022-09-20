

import aiohttp
import asyncio
from .exceptions import ConnectError, NotFound, Unsuccessful


class Session:
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept_Language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7',
        'Referer': 'https://google.com',
        'DNT': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36 OPR/85.0.4341.75'
    }

    def __init__(self, sleep_time=5) -> None:
        self.sleep_time = sleep_time

    async def __aenter__(self, *args):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, *args):
        await self.session.close()
        self.session = None

    async def fetch(self, url, expect_bs=True, retries=5):
        if retries == 0:
            raise Unsuccessful('Get 429 error too often')
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    if expect_bs:
                        text = await response.content.read()
                    else:
                        text = await response.read()
                    return text
                elif response.status == 404:
                    raise NotFound('Can\'t find given page')
                elif response.status == 429:
                    await asyncio.sleep(self.sleep_time)
                    return await self.fetch(url, expect_bs, retries=retries-1)
                else:
                    raise Unsuccessful(f'Status code is {response.status}')
        except aiohttp.ClientError as exc:
            raise ConnectError('Failed to connect') from exc
