from __future__ import annotations
from typing import Any
import asyncio
import aiohttp
from .exceptions import ConnectError, IncorrectMethod, NotFound, Unsuccessful


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
        sleep_time: float = 5,
        timeout: int | None = 360,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.session: aiohttp.ClientSession | None = None
        self.sleep_time = sleep_time
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.headers = headers or {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,"
            "image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Accept_Language": "en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7",
            "Referer": "https://google.com",
            "DNT": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            "(KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36 OPR/85.0.4341.75",
        }

    async def __aenter__(self, *args: Any) -> Session:
        self.session = aiohttp.ClientSession(headers=self.headers, timeout=self.timeout)
        return self

    async def __aexit__(self, *args: Any) -> None:
        assert isinstance(self.session, aiohttp.ClientSession)
        await self.session.close()
        self.session = None

    @staticmethod
    async def _apply_commands(
        response: aiohttp.ClientResponse, commands: list[str]
    ) -> aiohttp.ClientResponse:
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

    async def fetch(
        self, url: str, retries: int = 5, commands: list[str] | None = None
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
        if retries == 0:
            raise Unsuccessful("Get 429 error too often")
        try:
            assert isinstance(self.session, aiohttp.ClientSession)
            async with self.session.get(url) as response:
                if response.status == 200:
                    if commands:
                        response = await self._apply_commands(response, commands)
                    return response
                if response.status == 404:
                    raise NotFound("Can't find given page")
                if response.status == 429:
                    await asyncio.sleep(self.sleep_time)
                    return await self.fetch(url, retries - 1, commands)
                raise Unsuccessful(f"Status code is {response.status}")
        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            raise ConnectError(
                f"Failed to connect with following error - {exc}"
            ) from exc
        except AttributeError as error:
            raise Unsuccessful("Use this object as context manager") from error
