from abc import ABC, abstractmethod
import datetime
from pathlib import Path
from aiohttp import ClientResponse
from bs4 import BeautifulSoup
from manga_sales.data_scraping.dataclasses import Content
from manga_sales.data_scraping.session_context_manager import Session


class AbstractBase(ABC):
    def __init__(
        self,
    ) -> None:
        self.session = Session()

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

    def save_image(
        self, source: str, data_type: str, file: bytes, name: str, date: str
    ) -> None:
        image_path = f"manga_sales/static/images/{source}/{data_type}/"
        if file and name:
            path = Path(f"{image_path}{date}")
            path.mkdir(parents=True, exist_ok=True)
            with open(path / f"{name}", "wb") as open_file:
                open_file.write(file)

    @abstractmethod
    async def get_image(self, item: BeautifulSoup | str, date: str) -> str | None:
        pass

    @abstractmethod
    async def get_title(self, page: BeautifulSoup) -> tuple[str, BeautifulSoup]:
        pass


class MainItemDataParserAbstract(AbstractBase):
    _MAIN_URL: str = NotImplemented

    @abstractmethod
    async def get_main_info_page(self, title: str) -> BeautifulSoup:
        pass

    @abstractmethod
    def get_authors(self, page: BeautifulSoup) -> list[str]:
        pass

    @abstractmethod
    def get_publishers(self, page: BeautifulSoup) -> list[str]:
        pass


class ChartItemDataParserAbstract(AbstractBase):
    _CHART_URL: str = NotImplemented

    @abstractmethod
    async def get_data(self, date: str) -> list[Content] | None:
        pass

    @abstractmethod
    def get_rating(self, item: BeautifulSoup | str) -> int:
        """
        Get rating from given item
        """

    @abstractmethod
    def get_volume(self, item: BeautifulSoup | str) -> int | None:
        """
        Get rating from given item
        """

    @abstractmethod
    def get_release_date(self, item: BeautifulSoup | str) -> datetime.date | None:
        """
        Get release date from given item
        """

    @abstractmethod
    def get_sale(self, item: BeautifulSoup | str) -> int | None:
        """
        Get sales from given item
        """
