from __future__ import annotations
import datetime
import asyncio
import operator
import re
import uuid
from bs4 import BeautifulSoup
from src.data_scraping.aux_scrapers.abc import AuxDataParserAbstract
from src.data_scraping.dataclasses import Content
from src.data_scraping.exceptions import BSError, ConnectError, NotFound
from src.data_scraping.image_scrapers.abc import AbstractImageScraper
from src.data_scraping.image_scrapers.cdjapan import CDJapanImageScraper
from src.data_scraping.services.files_service import save_image

from src.data_scraping.session_context_manager import Session
from .abc import MainDataAbstractScraper


class OriconWeeklyScraper(MainDataAbstractScraper):
    """
    Class for collecting data from Oricon
    """

    SOURCE = "Oricon"
    SOURCE_TYPE = "Weekly"
    MAIN_URL: str = "https://www.oricon.co.jp/rank/obc/w/"
    _NUMBER_PAGES: int = 4

    def __init__(
        self,
        session: Session,
        main_info_parser: AuxDataParserAbstract,
    ) -> None:
        self.main_info_parser = main_info_parser
        super().__init__(session)

    # ------------helper methods for main methods------------
    @staticmethod
    def get_string_info(item: BeautifulSoup) -> str:
        return item.find("h2", {"class": "title"}).string

    def _get_original_title(self, item: BeautifulSoup) -> str:
        """Function for caputring name of title

        Args:
            item (BeautifulSoup): bs object inside which contains title

        Raises:
            BSError: occurs if an error occurs during parsing

        Returns:
            str: name of title
        """
        try:
            title_string = self.get_string_info(item)
            title_match = re.search(r"(?P<title>.+?)((?<=\s)\d+)", title_string)
            # as a rule, in Oricon, the volume number is always put at the end of the name,
            # so we capture everything that comes before it
            title_name = title_match["title"] if title_match else title_string
        except (AttributeError, IndexError) as error:
            raise BSError("Can't parse item to find title name") from error
        return title_name

    async def _get_list_raw_data(self, url: str) -> BeautifulSoup:
        data: BeautifulSoup = await self.fetch(url, commands=["content", "read"])
        list_items = data.find_all("section", {"class": "box-rank-entry"})
        if not list_items:
            raise BSError("Fail to find class with titles list")
        return list_items

    async def _get_aux_data(
        self, item: BeautifulSoup
    ) -> tuple[str, list[str], list[str]]:
        original_title = self._get_original_title(item)
        try:
            async with self.main_info_parser(title=original_title):
                name = self.main_info_parser.get_title()
                authors = self.main_info_parser.get_authors()
                publishers = self.main_info_parser.get_publishers()
        except Exception:  # pylint: disable = broad-except
            return original_title, [], []
        return name, authors, publishers

    async def create_content_item(
        self, index: int, item: BeautifulSoup, date: str
    ) -> Content:
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
        list_items = await self._get_list_raw_data(url)
        lst = []
        for i, item in enumerate(list_items, start=1):
            content = await self.create_content_item(i, item, date)
            lst.append(content)
        return lst

    # ------------main methods for collecting gata that invokes inside class------------
    async def get_data(self, date: str) -> list[Content]:
        pages: list[str] = [
            self.MAIN_URL + date + f"/p/{x}/" for x in range(1, self._NUMBER_PAGES)
        ]
        tasks = [asyncio.create_task(self._retrieve_data(page, date)) for page in pages]
        rating_list = await asyncio.gather(*tasks)
        return [x for y in rating_list for x in y] if rating_list else []

    def get_rating(self, item: BeautifulSoup) -> int | None:
        try:
            rating = int(item.find("p", {"class": "num"}).string)
        except (AttributeError, ValueError):
            return None
        return rating

    def get_volume(self, item: BeautifulSoup) -> int | None:
        volume = None
        try:
            lst = item.find("h2", {"class": "title"}).string.split()
        except AttributeError:
            return volume
        # iterate over all space-separated words from the title and
        # catch the first integer (usually this will be the volume)
        for piece in lst:
            try:
                volume = int(piece)
                break
            except ValueError:
                continue
        return volume

    def get_release_date(self, item: BeautifulSoup) -> datetime.date | None:
        try:
            text = (
                item.find("ul", {"class": "list"})
                .find(lambda tag: tag.name == "li" and "発売日" in tag.string)
                .string
            )
        except AttributeError:
            return None
        # fetch year and month
        regex_date = re.search(r"(?P<year>\d{4})年(?P<month>\d{2})月", text)
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
        regex_date = re.search(r"(?P<sold>[0-9,]+(?=部))", text)
        try:
            sold = int(regex_date["sold"].replace(",", "")) if regex_date else 0
        except ValueError:
            return None
        return sold

    async def _get_image(self, item: BeautifulSoup) -> bytes:
        img_url = item.find("p", {"class": "image"}).find("img").get("src")
        image_file = await self.fetch(img_url, ["read"], False)
        return image_file

    async def get_image(
        self, item: BeautifulSoup, date: str, name: str, volume: int
    ) -> str | None:
        str_info = self.get_string_info(item)
        image_parser = CDJapanImageScraper(self.session, str_info, name, volume)
        try:
            image = await image_parser.get_image()
        except NotFound:
            image = await self._get_image(item)
        name = f"{uuid.uuid4()}.jpg"
        save_image(self.SOURCE, self.SOURCE_TYPE, image, name, date)
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
            url = self.MAIN_URL + guess_date.strftime("%Y-%m-%d") + "/"
            try:
                await self.fetch(url, return_bs=False)
            except (ConnectionError, NotFound):
                count_days += 1
                continue
            return guess_date
        return None
