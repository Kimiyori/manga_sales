from __future__ import annotations
from abc import abstractmethod
import datetime
from bs4 import BeautifulSoup
from manga_scrapers.dataclasses import Content
from manga_scrapers.scrapers.image_scrapers.meta import AbstractImageScraper
from manga_scrapers.scrapers.meta import AbstractBase


class MainDataAbstractScraper(AbstractBase):
    """Abstract class for parser chart data"""

    SOURCE: str
    SOURCE_TYPE: str
    _MAIN_URL: str

    @abstractmethod
    async def get_data(self, date: str) -> list[Content] | None:
        """Main method for extract all data

        Args:
            date (str): string date to find url/page from which need scraping data

        Returns:
            list[Content] | None: list of Contents with data
        """

    @staticmethod
    @abstractmethod
    def get_rating(item: BeautifulSoup | str) -> int | None:
        """Get rating from given item

        Args:
            item (BeautifulSoup | str)

        Returns:
            int: rating
        """

    @staticmethod
    @abstractmethod
    def get_volume(item: BeautifulSoup | str) -> int | None:
        """
        Get volume from given item

        Args:
            item (BeautifulSoup | str)

        Returns:
            int | None: volume
        """

    @staticmethod
    @abstractmethod
    def get_release_date(item: BeautifulSoup | str) -> datetime.date | None:
        """
        Get release date from given item

        Args:
            item (BeautifulSoup | str)

        Returns:
            int | None: release date
        """

    @abstractmethod
    async def find_latest_date(
        self, date: datetime.date, action: str
    ) -> datetime.date | None:
        """Find last date from page

        Args:
            date (datetime.date)
            date_convert (bool, optional): bool value for deifint convert it to date type
            or remain it as string. Defaults to True.

        Returns:
            datetime.date | None
        """

    @abstractmethod
    async def get_image(  # pylint: disable=too-many-arguments
        self,
        item: BeautifulSoup,
        date: str,
        name: str,
        volume: int | None,
        image_scraper: AbstractImageScraper,
    ) -> str | None:
        """Get image file from item and save it

        Args:
            item (BeautifulSoup | str): item from which need to get either
                image or necessary data for it extraction
            date (str): date string

        Returns:
            str | None: name saved image
        """
