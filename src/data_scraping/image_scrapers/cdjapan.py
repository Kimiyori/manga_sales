import asyncio
import re
from bs4 import BeautifulSoup

from src.data_scraping.exceptions import ConnectError, NotFound, Unsuccessful
from src.data_scraping.image_scrapers.meta import AbstractImageScraper
from src.data_scraping.services.image_service import get_most_close
from src.data_scraping.utils.url import build_url, update_url


class CDJapanImageScraper(AbstractImageScraper):
    """Fetches image for manga title from cdjapan.co"""

    _MAIN_URL = build_url(
        scheme="https",
        netloc="www.cdjapan.co.jp",
        path=["searchuni"],
        query={"term.media_format": "BOOK"},
    )

    async def get_list_page(self) -> BeautifulSoup:
        """Get search page with titles found with search_name and volume

        Returns:
            BeautifulSoup: bs object fetched page
        """
        url = update_url(
            self._MAIN_URL,
            query={"q": f"{self.search_name} {self.volume if self.volume else ''}"},
        )
        page = await self.fetch(url, commands=["content", "read"])
        return page

    def get_page_url(self, list_page: BeautifulSoup) -> str:
        """Method that makes most important work -
            find needed title among many titles given in list_page

        Args:
            list_page (BeautifulSoup): list of titles in bs object

        Raises:
            NotFound: if no titles found(for exmaple empty list)

        Returns:
            str: link to the page of the title we are looking for
        """
        items_wrapper = list_page.find("ul", {"id": "js-search-result"})
        items_list = items_wrapper.findAll("li", {"class": "item"})
        # we use tuple as key to be sure that key is unique and we
        # will not override existing keys if? for example, there
        # wiil be items with the same name
        dict_names: dict[tuple[int, str], str] = {}
        # sometimes we given titles without volume and
        # for that case we need another pattern of matching
        pattern = (
            r"(?P<title>.+)\s(?P<volume>\d+)"
            if self.volume
            else r"^(?P<title>[^\[\(]+)\s"
        )
        for i, item in enumerate(items_list):
            full_name = item.find("span", {"class": "title-text"}).string
            title_match = re.search(
                pattern,
                full_name,
            )
            if not title_match:
                continue
            if (
                self.volume and int(title_match["volume"]) == self.volume
            ) or not self.volume:
                dict_names[(i, title_match["title"])] = item.find("a").get("href")
        most_similar = get_most_close(self.filter_name, list(dict_names.keys()))
        if most_similar:
            return dict_names[most_similar]
        raise NotFound

    async def get_page(self, list_page: BeautifulSoup) -> BeautifulSoup:
        """Get page for found title

        Args:
            list_page (BeautifulSoup): list from with we parse titles,
             found one that we need and fetch it

        Returns:
            BeautifulSoup: bs object of found title
        """
        url = self.get_page_url(list_page)
        page = await self.fetch(url, commands=["content", "read"])
        return page

    async def fetch_image(self, page: BeautifulSoup) -> bytes:
        """Method for fetching image

        Args:
            page (BeautifulSoup): page within which contains image

        Raises:
            Unsuccessful: if method fail to parse

        Returns:
            bytes: image
        """
        img_wrapper = page.find("div", {"id": "recs-sp-msg-container"})
        try:
            img_url = img_wrapper.find("img").get("src")
        except AttributeError:
            raise Unsuccessful
        if img_url.startswith("//"):
            img_url = "https:" + img_url
        try:
            img: bytes = await self.fetch(img_url, ["read"], False)
            assert isinstance(img, bytes)
        except AssertionError as error:
            raise Unsuccessful from error
        return img

    async def get_image(
        self, search_name: str, filter_name: str, volume: int | None, tries: int = 5
    ) -> bytes:
        self.search_name = search_name
        self.filter_name = filter_name
        self.volume = volume
        if tries == 0:
            raise Unsuccessful
        try:
            list_page = await self.get_list_page()
            page = await self.get_page(list_page)
            image = await self.fetch_image(page)
        except ConnectError:
            await asyncio.sleep(10)
            return await self.get_image(search_name, filter_name, volume, tries - 1)
        return image
