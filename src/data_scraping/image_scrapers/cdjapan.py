import asyncio
import re
from bs4 import BeautifulSoup
from src.data_scraping.exceptions import ConnectError, NotFound
from src.data_scraping.image_scrapers.abc import AbstractImageScraper
from src.data_scraping.services.image_service import get_most_close


class CDJapanImageScraper(AbstractImageScraper):
    _MAIN_URL = "https://www.cdjapan.co.jp/searchuni?term.media_format=BOOK&q="

    def create_url(self):
        return f"{self._MAIN_URL}{self.search_name} {self.volume}"

    async def get_list_page(self) -> BeautifulSoup:
        url = self.create_url()
        page = await self.fetch(url, commands=["content", "read"])
        return page

    def find_most_similar_title(
        self,
        list_page: BeautifulSoup,
    ) -> str:
        items_wrapper = list_page.find("ul", {"id": "js-search-result"})
        items_list = items_wrapper.findAll("li", {"class": "item"})
        dict_names = {}
        for item in items_list:
            title_match = re.search(
                r"(?P<title>.+)\s(?P<volume>\d+)(.+)?\s\(.+\)$",
                item.find("span", {"class": "title-text"}).string,
            )
            if title_match and int(title_match["volume"]) == self.volume:
                dict_names[title_match["title"]] = item.find("a").get("href")
        most_similar = get_most_close(self.filter_name, dict_names.keys())
        if most_similar:
            return dict_names[most_similar]
        raise NotFound

    def get_url(self, list_page: BeautifulSoup) -> str:
        url = self.find_most_similar_title(list_page)
        return url

    async def get_page(self, list_page: BeautifulSoup) -> BeautifulSoup:
        url = self.get_url(list_page)
        page = await self.fetch(url, commands=["content", "read"])
        return page

    async def _get_image(self, page: BeautifulSoup) -> bytes:
        img_wrapper = page.find("div", {"id": "recs-sp-msg-container"})
        img_url = img_wrapper.find("img").get("src")
        if img_url.startswith("//"):
            img_url = "https:" + img_url
        img = await self.fetch(img_url, ["read"], False)
        return img

    async def handle_page(self, list_page: BeautifulSoup):
        page = await self.get_page(list_page)
        image = await self._get_image(page)
        return image

    async def get_image(self, tries=5) -> bytes:
        if tries == 0:
            raise NotFound
        try:
            list_page = await self.get_list_page()
            image = await self.handle_page(list_page)
            assert isinstance(image, bytes)
            return image
        except ConnectError:
            await asyncio.sleep(10)
            await self.get_image(tries - 1)
        except AssertionError:
            raise NotFound
