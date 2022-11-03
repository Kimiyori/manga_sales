from abc import ABC
from bs4 import BeautifulSoup
from aiohttp import ClientResponse
from src.data_scraping.session_context_manager import Session


class AbstractBase(ABC):
    """Abstract class for scraping"""

    def __init__(self, session: Session) -> None:
        self.session = session

    async def fetch(
        self, url: str, commands: list[str] | None = None, return_bs: bool = True
    ) -> BeautifulSoup | ClientResponse | bytes:
        """
        Method for fetching given url

        Args:
            url:url from which exctract data
            commands: set fo commands that will be applied to response
            bs: return bs4 or pure response
        """
        response = await self.session.fetch(url, commands=commands)
        return BeautifulSoup(response, "html.parser") if return_bs else response
