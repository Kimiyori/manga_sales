from abc import ABC, abstractmethod
import datetime
import difflib
from pathlib import Path
import re
from aiohttp import ClientResponse
from bs4 import BeautifulSoup
from manga_sales.data_scraping.dataclasses import Content
from manga_sales.data_scraping.session_context_manager import Session


class AbstractScraper(ABC):
    def __init__(self) -> None:
        self.rating_list: list[Content] | None = []

    def save_image(self, file: bytes, name: str, date: str) -> None:
        lst_params: list[str] = re.findall("[A-Z][^A-Z]*", self.__class__.__name__)
        image_path = f"manga_sales/static/images/{lst_params[0].lower()}/{lst_params[1].lower()}/"
        if file and name:
            path = Path(f"{image_path}{date}")
            path.mkdir(parents=True, exist_ok=True)
            with open(path / f"{name}", "wb") as open_file:
                open_file.write(file)

    @abstractmethod
    async def get_data(self, date: str) -> list[Content] | None:
        """
        Main function for get all data
        """

    @abstractmethod
    async def _retrieve_data(self, url: str, date: str) -> list[Content]:
        """
        Get concrete piece of data
        """

    @abstractmethod
    def _get_rating(self, item: BeautifulSoup | str) -> int:
        """
        Get rating from given item
        """

    @abstractmethod
    def _get_volume(self, item: BeautifulSoup | str) -> int | None:
        """
        Get rating from given item
        """

    @abstractmethod
    async def _get_title(self, item: BeautifulSoup | str) -> tuple[str, BeautifulSoup]:
        """
        Get title from given item
        """

    @abstractmethod
    def _get_authors(self, item: BeautifulSoup | str) -> list[str]:
        """
        Get authors from given item
        """

    @abstractmethod
    def _get_publishers(self, item: BeautifulSoup | str) -> list[str]:
        """
        Get publishers from given item
        """

    @abstractmethod
    def _get_release_date(self, item: BeautifulSoup | str) -> datetime.date | None:
        """
        Get release date from given item
        """

    @abstractmethod
    def _get_sold_amount(self, item: BeautifulSoup | str) -> int | None:
        """
        Get sold from given item
        """

    @abstractmethod
    async def find_latest_date(
        self, date: datetime.date, date_convert: bool = True
    ) -> datetime.date | None:
        """
        Get concrete piece of data
        """


class RequestsClass:
    def __init__(self) -> None:
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


class MangaUpdatesAbstract(RequestsClass):
    _SEARCH_URL: str = "https://www.mangaupdates.com/series.html?search="

    async def _get_mangaupdates_page(self, original_name: str) -> BeautifulSoup:
        mangau_list = await self.fetch(
            url=self._SEARCH_URL + original_name, commands=["content", "read"]
        )
        # find most similar title
        mangau_item_link = self._get_most_similar_title(original_name, mangau_list)
        mangaupdates_page: BeautifulSoup = await self.fetch(
            url=mangau_item_link, commands=["content", "read"]
        )
        return mangaupdates_page

    @staticmethod
    def _get_most_similar_title(original_name: str, link: BeautifulSoup) -> str:

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

    @staticmethod
    def _get_authors(item: BeautifulSoup) -> list[str]:
        try:
            authors_tag = item.find("b", string="Author(s)").parent.find_next_sibling(
                "div"
            )
            authors_list = [author.string for author in authors_tag.find_all("u")]
        except AttributeError:
            return []
        return authors_list

    @staticmethod
    def _get_publishers(item: BeautifulSoup) -> list[str]:
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
