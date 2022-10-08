from abc import ABC, abstractmethod
import datetime
import difflib
from pathlib import Path
import re
from typing import Callable
from aiohttp import ClientResponse

from bs4 import BeautifulSoup
from manga_sales.data_scraping.dataclasses import Content
from manga_sales.data_scraping.session_context_manager import Session


class AbstractScraper(ABC):
    def __init__(self) -> None:

        self.session = Session()
        self.rating_list: list[Content] = []

    async def fetch(
        self, url: str, commands: list[str] | None = None, bs: bool = True
    ) -> BeautifulSoup | ClientResponse:
        """
        Method for fetching given url

        Args:
            url:url from which exctract data
            commands: set fo commands that will be applied to response
            bs: return bs4 or pure response
        """
        response = await self.session.fetch(url, commands=commands)
        return BeautifulSoup(response, "html.parser") if bs else response

    def save_image(self, file: ClientResponse, name: str) -> None:
        lst_params: list[str] = re.findall("[A-Z][^A-Z]*", self.__class__.__name__)
        image_path = f"manga_sales/static/images/{lst_params[0].lower()}/{lst_params[1].lower()}/"
        if file and name:
            p = Path(f"{image_path}{self.date}")
            p.mkdir(parents=True, exist_ok=True)
            with open(p / f"{name}", "wb") as f:
                f.write(file)

    @abstractmethod
    def _get_rating(self, item: BeautifulSoup) -> int:
        """
        Get rating from given item
        """
        pass

    @abstractmethod
    def _get_volume(self, item: BeautifulSoup) -> int | None:
        """
        Get rating from given item
        """
        pass

    @abstractmethod
    async def _get_title(self, item: BeautifulSoup) -> tuple[str, BeautifulSoup]:
        """
        Get title from given item
        """
        pass

    @abstractmethod
    def _get_authors(self, item: BeautifulSoup) -> list[str]:
        """
        Get authors from given item
        """
        pass

    @abstractmethod
    def _get_publishers(self, item: BeautifulSoup) -> list[str]:
        """
        Get publishers from given item
        """
        pass

    @abstractmethod
    def _get_release_date(self, item: BeautifulSoup) -> datetime.date | None:
        """
        Get release date from given item
        """
        pass

    @abstractmethod
    def _get_sold_amount(self, item: BeautifulSoup) -> int:
        """
        Get sold from given item
        """
        pass

    @abstractmethod
    async def get_data(self, date: str) -> list[Content]:
        """
        Main function for get all data
        """
        pass

    @abstractmethod
    async def retrieve_data(self, url: str) -> None:
        """
        Get concrete piece of data
        """
        pass

    @abstractmethod
    async def find_latest_date(
        self,
        date: datetime.date,
        operator: Callable[[datetime.date, datetime.timedelta], datetime.date],
    ) -> datetime.date | None:
        """
        Get concrete piece of data
        """
        pass


class MangaUpdatesAbstract:
    _SEARCH_URL: str = "https://www.mangaupdates.com/series.html?search="

    async def _get_mangaupdates_page(self, original_name: str) -> str:
        mangau_list = await self.fetch(
            url=self._SEARCH_URL + original_name, commands=["content", "read"]
        )
        # find most similar title
        mangau_item_link = self._get_most_similar_title(original_name, mangau_list)
        mangaupdates_page: BeautifulSoup = await self.fetch(
            url=mangau_item_link, commands=["content", "read"]
        )
        return mangaupdates_page

    def _get_most_similar_title(self, original_name: str, link: BeautifulSoup) -> str:

        items = link.find_all("div", {"class": "col-12 col-lg-6 p-3 text"})

        titles: dict[str, str] = {}

        for item in items:
            item = item.find("div", {"class": "text"})
            try:
                titles[item.find("b").string] = item.find("a")["href"]
            except KeyError:
                continue
        most_similar = difflib.get_close_matches(original_name, titles.keys())
        # return link to most similar if they exist
        # else return first in list fo titles
        return (
            titles[most_similar[0]] if most_similar else titles[list(titles.keys())[0]]
        )

    def _get_authors(self, item: BeautifulSoup) -> list[str]:
        try:
            authors_tag = item.find("b", string="Author(s)").parent.find_next_sibling(
                "div"
            )
            authors_list = [author.string for author in authors_tag.find_all("u")]
        except AttributeError:
            return []
        return authors_list

    def _get_publishers(self, item: BeautifulSoup) -> list[str]:
        try:
            publishers_tag = item.find(
                "b", string="Original Publisher"
            ).parent.find_next_sibling("div")
            publishers = [
                publisher.string for publisher in publishers_tag.find_all("u")
            ]
        except AttributeError:
            return []
        return publishers

    def _get_original_title(self, item: BeautifulSoup) -> str:
        raise NotImplementedError()

    async def _get_title(self, item: BeautifulSoup) -> tuple[str, BeautifulSoup]:
        original_name = self._get_original_title(item)
        title_page: BeautifulSoup = await self._get_mangaupdates_page(original_name)
        english_name: str = title_page.find(
            "span", {"class": "releasestitle tabletitle"}
        ).string
        return english_name, title_page
