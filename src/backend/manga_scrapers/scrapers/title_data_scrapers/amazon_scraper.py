# pylint: disable=no-member
from datetime import datetime, date

import re
from types import TracebackType
from typing import Any
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
from manga_scrapers.client_handler.session_context_manager import Session
from manga_scrapers.exceptions import ConnectError, NotFound
from manga_scrapers.scrapers.title_data_scrapers.meta import (
    _Self,
    AuxDataParserAbstract,
)
from manga_scrapers.utils.roman_calculate import roman_num_handler
from manga_scrapers.utils.url_handler import build_url, update_url
from manga_scrapers.utils.words_distance import get_most_close

STRING_MATCH = r"^(?P<title>.+?)\s?(?:\s|（|\()?(?P<volume>\d+|[MDCLXVI]+)?(?:\)|）)?巻?(?:【.+】)?\s?(?:\(|（).*(?:\)|）)"  # pylint: disable=line-too-long
VOLUME_MATCH = r"Volume\s(?P<volume>\d+)\s"


class AmazonParser(AuxDataParserAbstract):
    """Class for collecting data about title from MangaUpdates site"""

    _MAIN_URL: str = build_url(scheme="https", netloc="www.amazon.co.jp", path=[""])
    # ------------helper methods for main methods------------

    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.volume: int | None = None
        self.isbn: int
        self.publication_date: date

    async def __aenter__(self: _Self) -> _Self:
        """We using this class as context manager and
        passing it title name get main page for it"""
        self.page = await self.get_main_info_page()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: type[BaseException],
        exc_tb: type[TracebackType],
    ) -> None:
        del self.page
        # return await super().__aexit__(exc_type, exc_val, exc_tb)

    # ------------helper methods for main methods------------
    async def fetch(
        self, url: str, commands: list[str] | None = None, return_bs: bool = True
    ) -> Any:
        response = await self.session.fetch(url, commands=commands, sleep_time=3)
        return BeautifulSoup(response, "html.parser") if return_bs else response

    def _get_most_similar_title(
        self, link: BeautifulSoup
    ) -> dict[str, int | str | None | date] | None:
        """Method for finding most similar title in list of titles.

        Args:
            link (BeautifulSoup): bs4 page which contains list of titles.

        Returns:
            str: the returned string with the URL of the most similar title.
            if the method cannot find the most similar one, then it returns
            the first in the list.
        """
        wrapper_list = link.find("div", {"id": "search"})
        raw_titles_element = wrapper_list.findAll(
            "div",
            {
                "class": "a-section a-spacing-none puis-padding-right-small s-title-instructions-style"
            },
        )
        titles_data: dict[tuple[int, str], dict[str, int | str | None | date]] = {}
        for index, title_element in enumerate(raw_titles_element):
            title_string = title_element.find(
                "span", {"class": "a-size-medium a-color-base a-text-normal"}
            )
            string_match = re.search(STRING_MATCH, title_string.string)
            data_line = title_element.find("div", {"class": "a-row"})
            if not string_match or not data_line:
                continue
            volume = self._get_volume(data_line, string_match)
            if self.volume and volume and self.volume != int(volume):
                continue
            try:
                title_publication_date = datetime.strptime(
                    data_line.findChildren()[-1].string, "%Y/%m/%d"
                ).date()
            except ValueError:
                title_publication_date = datetime.strptime(
                    data_line.findChildren()[-1].string, "%b %d, %Y"
                ).date()
            if not self.publication_date or (
                self.publication_date
                and (
                    self.publication_date - relativedelta(months=+2)
                    <= title_publication_date
                    <= self.publication_date + relativedelta(months=+2)
                )
            ):
                assert isinstance(string_match.group("title"), str)
                titles_data[(index, string_match.group("title"))] = {
                    "volume": volume,
                    "link": self._MAIN_URL + title_string.parent["href"],
                    "publication_date": title_publication_date,
                }
        most_similar = get_most_close(self.title, list(titles_data.keys()))
        if most_similar:
            return titles_data[most_similar]
        return None

    @roman_num_handler
    def _get_volume(
        self, data_line: BeautifulSoup, string_match: re.Match[str]
    ) -> str | None:
        volume = None
        first_element = next(data_line.children)
        if (
            first_element.name == "a"
            and first_element["class"][0]
            == "a-link-normal s-underline-text s-underline-link-text s-link-style"
        ):
            match_volume = re.search(VOLUME_MATCH, first_element.string)
            volume = match_volume["volume"] if match_volume else None
        if not volume:
            volume = string_match["volume"]
        return volume

    # ------------main methods for collecting gata that invokes inside class------------
    async def get_main_info_page(self) -> BeautifulSoup:
        assert hasattr(self, "isbn")
        filter_list = await self.fetch(
            url=update_url(
                self._MAIN_URL,
                path=["s"],
                query={"k": self.isbn, "i": "stripbooks", "s": "date-desc-rank"},
            ),
            commands=["content", "read"],
        )
        most_similar_title = self._get_most_similar_title(filter_list)
        if not most_similar_title:
            raise NotFound
        if not self.volume and most_similar_title["volume"]:
            assert isinstance(most_similar_title["volume"], int)
            self.volume = most_similar_title["volume"]
        if not self.publication_date and most_similar_title["publication_date"]:
            assert isinstance(most_similar_title["publication_date"], date)
            self.publication_date = most_similar_title["publication_date"]
        assert isinstance(most_similar_title["link"], str)
        title_page: BeautifulSoup = await self.fetch(
            url=most_similar_title["link"], commands=["content", "read"]
        )
        return title_page

    def get_title(self) -> str:
        assert isinstance(self.title, str)
        return self.title

    def get_authors(self) -> list[str]:
        author_wrapper = self.page.find(
            "div", {"class": "a-section a-spacing-top-large singleAuthorSection"}
        )
        author_element = author_wrapper.find("h2")
        return [author_element.string]

    def get_publishers(self) -> list[str]:
        publisher_element = self.page.find(
            "div", {"id": "rpi-attribute-book_details-publisher"}
        )
        publisher_str = publisher_element.findAll("span")[-1].string
        return [publisher_str]

    def get_volume(self) -> int | None:
        return self.volume

    def get_publication_date(self) -> date | None:
        return self.publication_date

    # ------------methods that can be invoked somewhere outside------------
    async def get_image(self) -> bytes | None:
        try:
            img_url = self.page.find("img", {"id": "ebooksImgBlkFront"})["src"]
            if img_url is None:
                return None
            image_file = await self.fetch(img_url, ["read"], False)
            assert isinstance(image_file, bytes)
        except (ConnectError, AttributeError, AssertionError):
            return None
        return image_file
