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
        """Get

        Returns:
            BeautifulSoup: _description_
        """
        url = update_url(
            self._MAIN_URL,
            query={"q": f"{self.search_name} {self.volume if self.volume else ''}"},
        )
        page = await self.fetch(url, commands=["content", "read"])
        return page

    def get_page_url(self, list_page: BeautifulSoup) -> str:
        items_wrapper = list_page.find("ul", {"id": "js-search-result"})
        items_list = items_wrapper.findAll("li", {"class": "item"})
        dict_names: dict[str, str] = {}
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
                dict_names[tuple([i, title_match["title"]])] = item.find("a").get(
                    "href"
                )
        most_similar = get_most_close(self.filter_name, dict_names.keys())
        if most_similar:
            return dict_names[most_similar]
        raise NotFound

    async def get_page(self, list_page: BeautifulSoup) -> BeautifulSoup:
        url = self.get_page_url(list_page)
        page = await self.fetch(url, commands=["content", "read"])
        return page

    async def fetch_image(self, page: BeautifulSoup) -> bytes:
        img_wrapper = page.find("div", {"id": "recs-sp-msg-container"})
        img_url = img_wrapper.find("img").get("src")
        if img_url.startswith("//"):
            img_url = "https:" + img_url
        try:
            img: bytes = await self.fetch(img_url, ["read"], False)
            assert isinstance(img, bytes)
        except AssertionError as error:
            raise Unsuccessful from error
        return img

    async def get_image(self, tries: int = 5) -> bytes:
        if tries == 0:
            raise Unsuccessful
        try:
            list_page = await self.get_list_page()
            page = await self.get_page(list_page)
            image = await self.fetch_image(page)
        except ConnectError:
            await asyncio.sleep(10)
            return await self.get_image(tries - 1)
        return image