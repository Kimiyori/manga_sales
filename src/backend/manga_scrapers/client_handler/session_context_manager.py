from __future__ import annotations
import random
from types import TracebackType
from typing import Any
import asyncio
import aiohttp
from config.config import PROXY_URL
from manga_scrapers.exceptions import (
    ConnectError,
    IncorrectMethod,
    NotFound,
    Unsuccessful,
)

MAX_CONCURRENCY = 15
MAX_CONCURRENCY_PER_HOST = 5
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}


class Session:
    """
    Object for connect to aiohttp ClientSession and handle context manager
    Args:
        sleep_time: Sets sleep time in case of error 429 for too many requests.
        timeout: Set timeout for ClientTimeout class.
        headers: Set headers or can be omitted and defalt headers defined
        in class will be used.
    """

    def __init__(
        self,
        timeout: int | None = 360,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.connector = aiohttp.TCPConnector(
            limit=MAX_CONCURRENCY, limit_per_host=MAX_CONCURRENCY_PER_HOST
        )
        self.session: aiohttp.ClientSession
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.headers = headers or HEADERS

    async def __aenter__(self) -> Session:
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=self.timeout,
            connector=self.connector,
        )
        self.proxy_list = await self.get_proxy()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: type[BaseException],
        exc_tb: type[TracebackType],
    ) -> None:
        await self.session.close()

    def choose_proxy(self) -> int:
        return random.randint(0, len(self.proxy_list) - 1)

    def rotate_proxy(self, proxy_index: int, initial_index: int) -> int:
        proxy_index = (proxy_index + 1) % len(self.proxy_list)
        if proxy_index == initial_index:
            raise ConnectError("Failed to connect, perhabs due to invalid proxies")
        return proxy_index

    async def get_proxy(self) -> list[str | None]:
        proxy_list: list[str | None] = [None]
        try:
            async with self.session.get(f"{PROXY_URL}/getproxy") as response:
                content = await response.json()
                if content:
                    proxy_names = content["list"].keys()
                    for name in proxy_names:
                        proxy_data = content["list"][name]
                        proxy_list.append(
                            f"http://{proxy_data['user']}:{proxy_data['pass']}@{proxy_data['host']}:{proxy_data['port']}"
                        )
                return proxy_list
        except aiohttp.ClientResponseError:
            await asyncio.sleep(1)
            return await self.get_proxy()

    @staticmethod
    async def _apply_commands(
        response: aiohttp.ClientResponse, commands: list[str]
    ) -> Any:
        for command in commands:
            try:
                response: Any = getattr(response, command)  # type: ignore
                try:
                    response = await response()  # type: ignore
                except TypeError:
                    pass
            except AttributeError as error:
                raise IncorrectMethod(
                    "Response object does not have" f"given attribute - {command}"
                ) from error
        return response

    async def _get(
        self,
        url: str,
        proxy_index: int,
        initial_index: int,
        commands: list[str] | None = None,
        sleep_time: int | None = None,
    ) -> Any:
        try:
            async with self.session.get(
                url, proxy=self.proxy_list[proxy_index]
            ) as response:
                if response.status == 200:
                    if commands:
                        response = await self._apply_commands(response, commands)
                    return response
                if response.status == 404:
                    raise NotFound("Can't find given page")
                if response.status == 429:
                    print(f"{url} - {sleep_time} = {response.status}")
                    if not sleep_time:
                        sleep_time = 1
                    await asyncio.sleep(sleep_time)
                    sleep_time += 1
                    return await self.fetch(url, commands, sleep_time)
                if response.status == 503:
                    self.rotate_proxy(proxy_index, initial_index)
                    return await self._get(
                        url, proxy_index, initial_index, commands, sleep_time
                    )
                raise Unsuccessful(f"Status code is {response.status}")
        except (aiohttp.ClientError, asyncio.TimeoutError):
            self.rotate_proxy(proxy_index, initial_index)
            return await self._get(
                url, proxy_index, initial_index, commands, sleep_time
            )

    async def fetch(
        self, url: str, commands: list[str] | None = None, sleep_time: int | None = None
    ) -> Any:
        """
        Method for handling requests/responses
        Args:
            url: Url to which the request should be sent
            retries: Set how many times we can get a 429 error (default 5)
                        after which we will raise the error.
            commands: set list for the command that is invoked on the response
            object. For example, ['content','read']
                would be called on the response as follows -
                response.content.read(). Can be omitted
                and then method returns just response object.
        """
        if sleep_time:
            await asyncio.sleep(sleep_time)
        proxy_index = initial_index = self.choose_proxy()
        return await self._get(url, proxy_index, initial_index, commands, sleep_time)
