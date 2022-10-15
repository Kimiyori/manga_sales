from abc import ABC, abstractmethod
import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from aiohttp import ClientResponse
from manga_sales.data_scraping.dataclasses import Content
from manga_sales.data_scraping.session_context_manager import Session


class AbstractBase(ABC):
    """Abstract class for scraping"""

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

    @staticmethod
    def save_image(
        source: str, data_type: str, file: bytes, name: str, date: str
    ) -> None:
        """Saves image in path defined with source and data_type arguments with following path:
         Path: 'manga_sales/static/images/{source}/{data_type}/'

        Args:
            source (str): type of source data (oricon etc)
            data_type (str): data type (weekly, monthly etc)
            file (bytes): image file that need to be saved
            name (str): file name
            date (str): date in string format
        """
        # confirm that all arguments needed for path are str type
        assert (
            isinstance(source, str)
            and isinstance(data_type, str)
            and isinstance(date, str)
        )
        image_path = (
            f"manga_sales/static/images/{source.lower()}/{data_type.lower()}/{date}"
        )
        if file and name:
            path = Path(image_path)
            # ensure that given path exist or create it
            path.mkdir(parents=True, exist_ok=True)
            with open(path / f"{name}", "wb") as open_file:
                open_file.write(file)

    @abstractmethod
    async def get_image(self, item: BeautifulSoup | str, date: str) -> str | None:
        """Get image file from item and save it

        Args:
            item (BeautifulSoup | str): item from which need to get either
                image or necessary data for it extraction
            date (str): date string

        Returns:
            str | None: name saved image
        """

    @abstractmethod
    async def get_title(self, page: BeautifulSoup) -> tuple[str, BeautifulSoup]:
        """Get title from page and get page for main info

        Args:
            page (BeautifulSoup): bs item from which extract title

        Returns:
            tuple[str, BeautifulSoup]: (title name, page with main info)
        """

    @abstractmethod
    async def find_latest_date(
        self, date: datetime.date, date_convert: bool = True
    ) -> datetime.date | None:
        """Find last date from page

        Args:
            date (datetime.date)
            date_convert (bool, optional): bool value for deifint convert it to date type
            or remain it as string. Defaults to True.

        Returns:
            datetime.date | None
        """


class MainItemDataParserAbstract(AbstractBase):
    """Abstract class for parser main data"""

    _MAIN_URL: str = NotImplemented

    @abstractmethod
    async def get_main_info_page(self, title: str) -> BeautifulSoup:
        """Get page from with can be collected main info
        Args:
            title (str): the name of the title of the page need to get
        Returns:
            BeautifulSoup: bs page
        """

    @staticmethod
    @abstractmethod
    def get_authors(page: BeautifulSoup) -> list[str]:
        """Parse page to get list of authors from it

        Args:
            page (BeautifulSoup): bs page

        Returns:
            list[str]: list with strings of authors name
        """

    @staticmethod
    @abstractmethod
    def get_publishers(page: BeautifulSoup) -> list[str]:
        """Parse page to get list of publishers from it

        Args:
            page (BeautifulSoup): bs page

        Returns:
            list[str]: list with strings of publishers name
        """


class ChartItemDataParserAbstract(AbstractBase):
    """Abstract class for parser chart data"""

    _CHART_URL: str = NotImplemented

    @abstractmethod
    async def get_data(self, date: str) -> list[Content] | None:
        """Main method for extract all data

        Args:
            date (str): string date to find url/page from which need scraping data

        Returns:
            list[Content] | None: list of Contents with data
        """

    @abstractmethod
    def get_rating(self, item: BeautifulSoup | str) -> int:
        """Get rating from given item

        Args:
            item (BeautifulSoup | str)

        Returns:
            int: rating
        """

    @abstractmethod
    def get_volume(self, item: BeautifulSoup | str) -> int | None:
        """
        Get volume from given item

        Args:
            item (BeautifulSoup | str)

        Returns:
            int | None: volume
        """

    @abstractmethod
    def get_release_date(self, item: BeautifulSoup | str) -> datetime.date | None:
        """
        Get release date from given item

        Args:
            item (BeautifulSoup | str)

        Returns:
            int | None: release date
        """

    @abstractmethod
    def get_sale(self, item: BeautifulSoup | str) -> int | None:
        """
        Get sales from given item

        Args:
            item (BeautifulSoup | str)

        Returns:
            int | None: sale
        """
