from __future__ import annotations
import datetime
import asyncio
import operator
import re
from bs4 import BeautifulSoup
from dependency_injector.wiring import Provide, inject, Closing

from manga_scrapers.scrapers.title_data_scrapers.meta import AuxDataParserAbstract
from manga_scrapers.containers.title_data_container import AuxScrapingContainer
from manga_scrapers.containers.image_container import ImageScrapingContainer
from manga_scrapers.dataclasses import Content
from manga_scrapers.exceptions import BSError, NotFound, Unsuccessful
from manga_scrapers.scrapers.image_scrapers.meta import AbstractImageScraper
from manga_scrapers.scrapers.rating_scrapers.meta import MainDataAbstractScraper
from manga_scrapers.services.files_service import save_image
from manga_scrapers.utils.url_handler import build_url, update_url

TITLE_DATE_PATTERN_MATCH = r"(?P<year>\d{4})年(?P<month>\d{2})月"
TITLE_VOLUME_PATTERN_MATCH = r"\d+(?!.*\d+)"
TITLE_NAME_PATTERN_MATCH = r"(?P<title>.+)\s\d+"
TITLE_SALES_PATTERN_MATCH = r"(?P<sold>[0-9,]+(?=部))"


class OriconWeeklyScraper(MainDataAbstractScraper):
    """
    Class for collecting data from Oricon
    """

    SOURCE = "Oricon"
    SOURCE_TYPE = "Weekly"
    MAIN_URL: str = build_url(
        scheme="https",
        netloc="www.oricon.co.jp",
        path=["rank", "obc", "w"],
    )
    _NUMBER_PAGES: int = 4

    # ------------helper methods for main methods------------
    @staticmethod
    def _get_original_title(item: BeautifulSoup) -> str:
        """Function for caputring name of title

        Args:
            item (BeautifulSoup): bs object inside which contains title

        Raises:
            BSError: occurs if an error occurs during parsing

        Returns:
            str: name of title
        """
        try:
            title_string: str = item.find("h2", {"class": "title"}).string
            title_match = re.search(TITLE_NAME_PATTERN_MATCH, title_string)
            # as a rule, in Oricon, the volume number is always put at the end of the name,
            # so we capture everything that comes before it
            title_name = title_match["title"] if title_match else title_string
            title_name = title_name.replace("。", "")
            assert title_name
        except (AssertionError, AttributeError, IndexError) as error:
            raise BSError("Can't parse item to find title name") from error
        return title_name

    async def _get_list_raw_data(self, url: str) -> BeautifulSoup:
        """Fetches page with all titles

        Args:
            url (str): oricon url

        Raises:
            BSError: raises if bs fails to parse fetched data

        Returns:
            BeautifulSoup: page
        """
        data: BeautifulSoup = await self.fetch(url, commands=["content", "read"])
        list_items = data.find_all("section", {"class": "box-rank-entry"})
        if not list_items:
            raise BSError("Fail to find class with titles list")
        return list_items

    @inject
    async def _get_aux_data(
        self,
        item: BeautifulSoup,
        aux_scraper: AuxDataParserAbstract = Closing[
            Provide[AuxScrapingContainer.manga_updates_scraper]
        ],
    ) -> tuple[str, list[str], list[str]]:
        """Fetch and parse additional data about given title,
        including its name in english(romaji) and authors and publishers

        Args:
            item (BeautifulSoup): page

        Returns:
            tuple[str, list[str], list[str]]: name, authors, publishers
        """
        original_title = self._get_original_title(item)
        try:
            async with aux_scraper(title=original_title):
                name = aux_scraper.get_title()
                authors = aux_scraper.get_authors()
                publishers = aux_scraper.get_publishers()
        except Exception:  # pylint: disable = broad-except
            return original_title, [], []
        return name, authors, publishers

    async def create_content_item(
        self, index: int, item: BeautifulSoup, date: str
    ) -> Content:
        """Collect all data about given title

        Args:
            index (int): index that passed from  _retrieve_data method.
            Used to put in place a rating if it can't be obtained

            item (BeautifulSoup): page
            date (str): date current chart

        Returns:
            Content: dataclass that contains all fetched data
        """
        rating = self.get_rating(item)
        volume = self.get_volume(item)
        name, authors, publishers = await self._get_aux_data(item)
        image = await self.get_image(item, date, name, volume)
        content = Content(
            name=name,
            volume=volume,
            image=image,
            authors=authors,
            publishers=publishers,
            release_date=self.get_release_date(item),
            rating=rating if rating else index,
            sales=self.get_sales(item),
        )
        return content

    async def _retrieve_data(self, url: str, date: str) -> list[Content]:
        """Method for collecting all data about all titles for given page in single list

        Args:
            url (str): url from witch need to collect data
            date (str): date current chart

        Returns:
            list[Content]: list fo contents
        """
        list_items = await self._get_list_raw_data(url)
        tasks = [
            asyncio.create_task(self.create_content_item(i, item, date))
            for i, item in enumerate(list_items, start=1)
        ]
        lst = await asyncio.gather(*tasks)
        return lst

    # ------------main methods for collecting gata that invokes inside class------------
    async def get_data(self, date: str) -> list[Content]:
        pages: list[str] = [
            update_url(self.MAIN_URL, path=[date, "p", str(x)], trailing_slash=True)
            for x in range(1, self._NUMBER_PAGES)
        ]
        tasks = [asyncio.create_task(self._retrieve_data(page, date)) for page in pages]
        rating_list = await asyncio.gather(*tasks)
        return [x for y in rating_list for x in y] if rating_list else []

    @staticmethod
    def get_rating(item: BeautifulSoup) -> int | None:
        try:
            rating = int(item.find("p", {"class": "num"}).string)
        except (AttributeError, ValueError):
            return None
        return rating

    @staticmethod
    def get_volume(item: BeautifulSoup) -> int | None:
        volume = None
        try:
            full_name = item.find("h2", {"class": "title"}).string
        except AttributeError:
            return volume
        re_match = re.search(TITLE_VOLUME_PATTERN_MATCH, full_name)
        return int(re_match[0]) if re_match else None

    @staticmethod
    def get_release_date(item: BeautifulSoup) -> datetime.date | None:
        try:
            text = (
                item.find("ul", {"class": "list"})
                .find(lambda tag: tag.name == "li" and "発売日" in tag.string)
                .string
            )
        except AttributeError:
            return None
        # fetch year and month
        regex_date = re.search(TITLE_DATE_PATTERN_MATCH, text)
        try:
            date = (
                datetime.date(int(regex_date["year"]), int(regex_date["month"]), 1)
                if regex_date
                else None
            )
        except ValueError:
            return None
        return date

    @staticmethod
    def get_sales(item: BeautifulSoup) -> int | None:
        try:
            text = (
                item.find("ul", {"class": "list"})
                .find(lambda tag: tag.name == "li" and "推定売上部数" in tag.string)
                .string
            )
        except AttributeError:
            return None
        regex_date = re.search(TITLE_SALES_PATTERN_MATCH, text)
        try:
            sold = int(regex_date["sold"].replace(",", "")) if regex_date else 0
        except ValueError:
            return None
        return sold

    async def _get_image(self, item: BeautifulSoup) -> bytes:
        img_url = item.find("p", {"class": "image"}).find("img").get("src")
        image_file = await self.fetch(img_url, ["read"], False)
        assert isinstance(image_file, bytes)
        return image_file

    @inject
    async def get_image(  # pylint: disable=too-many-arguments
        self,
        item: BeautifulSoup,
        date: str,
        name: str,
        volume: int | None,
        image_scraper: AbstractImageScraper = Closing[
            Provide[ImageScrapingContainer.cdjapan_scraper]
        ],
    ) -> str | None:
        str_info = item.find("h2", {"class": "title"}).string
        try:
            image = await image_scraper.get_image(str_info, name, volume)
        except (Unsuccessful, NotFound):
            image = await self._get_image(item)
        name = save_image(self.SOURCE, self.SOURCE_TYPE, image, date)
        return name

    # ------------methods that can be invoked somewhere outside------------
    async def find_latest_date(
        self,
        date: datetime.date,
        action: str,
    ) -> datetime.date | None:
        count_days = 1
        assert action in ("forward", "backward")
        operator_action = operator.add if action == "forward" else operator.sub
        while count_days <= 7:
            guess_date: datetime.date = operator_action(
                date, datetime.timedelta(days=count_days)
            )
            url = update_url(
                self.MAIN_URL,
                path=[guess_date.strftime("%Y-%m-%d")],
                trailing_slash=True,
            )
            try:
                await self.fetch(url, return_bs=False)
            except (ConnectionError, NotFound):
                count_days += 1
                continue
            return guess_date
        return None
