from __future__ import annotations
import difflib
from types import TracebackType
from bs4 import BeautifulSoup
from src.data_scraping.exceptions import ConnectError
from src.data_scraping.services.image_service import get_most_close
from .abc import _Self, AuxDataParserAbstract


class MangaUpdatesParser(AuxDataParserAbstract):
    """Class for collecting data about title from MangaUpdates site"""

    _MAIN_URL: str = "https://www.mangaupdates.com/series.html?filter=no_oneshots&type=manga&perpage=10&search="


    # ------------helper methods for main methods------------

    async def __aenter__(self: _Self) -> _Self:
        page = await self.get_main_info_page()
        self.page = page
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: type[BaseException],
        exc_tb: type[TracebackType],
    ) -> None:
        del self.page
        return await super().__aexit__(exc_type, exc_val, exc_tb)

    # ------------helper methods for main methods------------
    def _get_most_similar_title(self, link: BeautifulSoup) -> str:
        """Method for finding most similar title in list of titles.

        Args:
            link (BeautifulSoup): bs4 page which contains list of titles.

        Returns:
            str: the returned string with the URL of the most similar title.
            if the method cannot find the most similar one, then it returns
            the first in the list.
        """
        items = link.find_all("div", {"class": "col-12 col-lg-6 p-3 text"})
        assert len(items) > 0
        titles: dict[str, str] = {}
        for item in items:
            item = item.find("div", {"class": "text"})
            try:
                titles[item.find("b").string] = item.find("a")["href"]
            except (KeyError, AttributeError):
                continue
        assert len(titles) > 0
        most_similar = get_most_close(self.title, titles.keys())
        # return link to most similar if it exist
        # else return first in list of titles
        return (
            titles[most_similar] if most_similar else titles[list(titles.keys())[0]]
        )

    # ------------main methods for collecting gata that invokes inside class------------
    async def get_main_info_page(self) -> BeautifulSoup:
        filter_list = await self.fetch(
            url=self._MAIN_URL + self.title, commands=["content", "read"]
        )
        most_similar_title = self._get_most_similar_title(filter_list)
        title_page: BeautifulSoup = await self.fetch(
            url=most_similar_title, commands=["content", "read"]
        )
        return title_page

    def get_title(self) -> str:
        try:
            title: str = self.page.find(
                "span", {"class": "releasestitle tabletitle"}
            ).string
        except AttributeError:
            # if error occur, then return original name
            return self.title
        return title

    def get_authors(self) -> list[str]:
        try:
            authors_tag = self.page.find(
                "b", string="Author(s)"
            ).parent.find_next_sibling("div")
            authors_list = [author.string for author in authors_tag.find_all("u")]
        except AttributeError:
            return []
        return authors_list

    def get_publishers(self) -> list[str]:
        try:
            publishers_tag = self.page.find(
                "b", string="Original Publisher"
            ).parent.find_next_sibling("div")
            publishers = [
                publisher.string for publisher in publishers_tag.find_all("u")
            ]
        except AttributeError:
            return []
        return publishers

    # ------------methods that can be invoked somewhere outside------------
    async def get_image(self) -> bytes | None:
        try:
            img_url = self.page.find("img", {"class": "img-fluid"}).get("src")
            if img_url is None:
                return None
            image_file = await self.fetch(img_url, ["read"], False)
            assert isinstance(image_file, bytes)
        except (ConnectError, AttributeError, AssertionError):
            return None
        return image_file
