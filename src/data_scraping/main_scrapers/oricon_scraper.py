from __future__ import annotations
import datetime
import asyncio
import re
import uuid
from bs4 import BeautifulSoup
from src.data_scraping.aux_scrapers.abc import AuxDataParserAbstract
from src.data_scraping.dataclasses import Content
from src.data_scraping.exceptions import BSError, ConnectError, NotFound
from src.data_scraping.services.images_service import save_image
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
        self, session: Session, main_info_parser: AuxDataParserAbstract
    ) -> None:
        self.main_info_parser = main_info_parser
        super().__init__(session)

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
            split_name: list[str] = item.find("h2", {"class": "title"}).string.split()
            # as a rule, in Oricon, the volume number is always put at the end of the name,
            # so we capture everything that comes before it
            japanese_name = (
                " ".join(x for x in split_name[:-1])
                if len(split_name) > 1
                else split_name[0]
            )
        except (AttributeError, IndexError) as error:
            raise BSError("Can't parse item to find title name") from error
        return japanese_name

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
        image = await self.get_image(item, date)
        name, authors, publishers = await self._get_aux_data(item)
        content = Content(
            name=name,
            volume=self.get_volume(item),
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

    async def get_image(self, item: BeautifulSoup, date: str) -> str | None:
        def create_name(url: str) -> str:
            reg = re.search(r".(\w+)$", url)
            extension = reg.group(1) if reg else "jpg"
            name = f"{uuid.uuid4()}.{extension}"
            return name

        try:
            img_url = item.find("p", {"class": "image"}).find("img").get("src")
            if img_url is None:
                return None
            name = create_name(img_url)
            image_file = await self.fetch(img_url, ["read"], False)
        except (ConnectError, AttributeError):
            return None
        assert isinstance(image_file, bytes)
        save_image(self.SOURCE, self.SOURCE_TYPE, image_file, name, date)
        return name

    # ------------methods that can be invoked somewhere outside------------
    async def find_latest_date(
        self, date: datetime.date, date_convert: bool = True
    ) -> datetime.date | str | None:
        count_days = 1
        while count_days <= 7:
            guess_date = date + datetime.timedelta(days=count_days)
            url = self.MAIN_URL + guess_date.strftime("%Y-%m-%d") + "/"
            try:
                await self.fetch(url, return_bs=False)
            except (ConnectionError, NotFound):
                count_days += 1
                continue
            return guess_date if date_convert else guess_date.strftime("%Y-%m-%d")
        return None
