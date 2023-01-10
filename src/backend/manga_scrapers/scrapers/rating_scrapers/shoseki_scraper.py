from __future__ import annotations
import datetime
import operator
import re
import unicodedata
from bs4 import BeautifulSoup
from dependency_injector.wiring import Provide, inject, Closing

from manga_scrapers.scrapers.rating_scrapers.meta import MainDataAbstractScraper
from manga_scrapers.scrapers.title_data_scrapers.amazon_scraper import AmazonParser
from manga_scrapers.scrapers.title_data_scrapers.meta import AuxDataParserAbstract
from manga_scrapers.containers.title_data_container import AuxScrapingContainer
from manga_scrapers.containers.image_container import ImageScrapingContainer
from manga_scrapers.dataclasses import Content
from manga_scrapers.exceptions import NotFound, Unsuccessful
from manga_scrapers.scrapers.image_scrapers.meta import AbstractImageScraper
from manga_scrapers.services.files_service import save_image
from manga_scrapers.utils.date_helper import convert_str_to_date
from manga_scrapers.utils.url_handler import build_url

LIST_DATE_PATERN_MATCH = r"^([0-9]+)\/([0-9]+)\/([0-9]+)\s:\s.+"
TITLE_NAME_PATTERN_MATCH = r"^(?P<title>.+?)\s(?:\d+|ＫＡＤＯＫ)?[:\D]+\s[\d.]+$"
TITLE_VOLUME_PATTERN_MATCH = r"(?P<volume>\d+)\s[\s\w\d]+\s[\d.]+$"
TITLE_DATE_PATERN_MATCH = (
    r"^(?P<year>[0-9]{4})[-\/\.](?P<month>[0-9]{1,2})[-\/\.]?(?P<day>[0-9]{0,2})"
)


class ShosekiWeeklyScraper(MainDataAbstractScraper):
    """
    Class for collecting data from Shoseki
    """

    SOURCE = "Shoseki"
    SOURCE_TYPE = "Weekly"
    MAIN_URL: str = build_url(
        scheme="http",
        netloc="shosekiranking.blog.fc2.com",
        path=[
            "blog-category-6.html",
        ],
    )

    # ------------helper methods for main methods------------

    async def _get_list_raw_data(self, url: str) -> list[list[str]]:
        """Extracts all the required data from the page

        Args:
            url (str): url from which nned get data
        Raises:
            error: raises Attribute error if beatifulsoup fial to parse

        Returns:
            list[list[str]]: reutn data with following pattern:
            [[rating,ISBN,title string with name and also volume and
            date release if exist in solid line]]
        """
        page: BeautifulSoup = await self.fetch(url, commands=["content", "read"])
        try:
            body = page.find("div", {"class": "content"}).find(
                "div", {"class": "entry_body"}
            )
        except AttributeError as error:
            raise error
        text_items: list[str] = body.get_text(strip=True, separator="\n").splitlines()
        list_items: list[list[str]] = [
            [unicodedata.normalize("NFKC", x) for x in text_items[i : i + 3]]
            for i in range(0, 90, 3)
            if text_items[i : i + 3]
        ]
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

    @inject
    async def _get_volume_from_amazon(
        self,
        item: str,
        isbn: int,
        release_date: datetime.date | None,
        aux_scraper: AmazonParser = Closing[
            Provide[AuxScrapingContainer.amazon_scraper]
        ],
    ) -> int | None:
        original_title = self._get_original_title(item)
        try:
            async with aux_scraper(
                title=original_title,
                volume=None,
                isbn=isbn,
                publication_date=release_date,
            ) as scraper:
                volume = scraper.get_volume()
        except NotFound:
            return None
        assert not volume or isinstance(volume, int)
        return volume

    async def create_content_item(
        self, index: int, row: list[str], date: str
    ) -> Content:
        """Collect all data required for signle item and wrapp in 'Content' dataclass

        Args:
            index (int): index for indicate rating in case fail to catch it
            row (list[str]): row with info about give title
            in form: [id,ISBN,'title,volume,date and publisher']
            date (str): current date

        Returns:
            Content: Content instance
        """
        rating = self.get_rating(row[0])
        volume = self.get_volume(row[2])
        release_date = self.get_release_date(row[2])
        if not volume:
            volume = await self._get_volume_from_amazon(
                row[2], int(row[1]), release_date
            )
        name, authors, publishers = await self._get_aux_data(row[2])
        image = await self.get_image(row, date=date, name=name, volume=volume)
        content = Content(
            name=name,
            volume=volume,
            image=image,
            authors=authors,
            publishers=publishers,
            release_date=release_date,
            rating=rating if rating else index,
        )
        return content

    async def _retrieve_data(self, url: str, date: str) -> list[Content]:
        """Method for iterating of list of data and collecting data for each of them

        Args:
            url (str): url from with need collect data
            date (str): cureent date

        Returns:
            list[Content]: list with Contents instances
        """
        list_items = await self._get_list_raw_data(url)
        lst = []
        for i, row in enumerate(list_items):
            content = await self.create_content_item(i, row, date)
            lst.append(content)
        return lst

    async def _get_data_url(self, date: str) -> str | None:
        """method for finding url to ratign for either given date
        or most close date that comes before ti

        Args:
            date (str)

        Raises:
            error:  raises Attribute error if an error occurs while parsing

        Returns:
            str | None: return url to found url or none, of that url doesnt exist
        """
        main_page: BeautifulSoup = await self.fetch(
            self.MAIN_URL, commands=["content", "read"]
        )
        try:
            dates: list[BeautifulSoup] = main_page.find(
                "ul", {"class": "list_body"}
            ).find_all("li")
        except AttributeError as error:
            raise error
        for date_obj in dates:
            guess_date: str = re.sub(
                LIST_DATE_PATERN_MATCH,
                r"\g<1>-\g<2>-\g<3>",
                date_obj.text,
            )
            if date == guess_date:
                url: str = date_obj.find("a")["href"]
                return url
        return None

    @staticmethod
    def _get_original_title(item: str) -> str:
        """Method for extracting title name from string

        Args:
            item (str): string with title name, volume, publisher and publication date

        Returns:
            str: title name
        """
        reg = re.search(TITLE_NAME_PATTERN_MATCH, item)
        return reg.group("title") if reg else item

    # ------------main methods for collecting gata that invokes inside class------------
    async def get_data(self, date: str) -> list[Content] | None:
        url = await self._get_data_url(date)
        rating_list = await self._retrieve_data(url, date) if url else None
        return rating_list

    async def _get_image(self, item: str) -> bytes:
        amazon_url = build_url(
            scheme="https",
            netloc="www.amazon.co.jp",
            path=["s"],
            query={"i": "stripbooks", "ref": "nb_sb_noss", "k": item},
        )
        page_image: BeautifulSoup = await self.fetch(
            amazon_url, commands=["content", "read"]
        )
        img_url = page_image.find("img", {"class": "s-image"})["src"]
        image_file: bytes = await self.fetch(img_url, ["read"], False)
        return image_file

    @inject
    async def get_image(  # pylint: disable=too-many-arguments
        self,
        item: list[str],
        date: str,
        name: str,
        volume: int | None,
        image_scraper: AbstractImageScraper = Closing[
            Provide[ImageScrapingContainer.cdjapan_scraper]
        ],
    ) -> str | None:
        str_info = f"{self._get_original_title(item[2])} {volume}"
        try:
            image = await image_scraper.get_image(str_info, name, volume)
        except (Unsuccessful, NotFound):
            image = await self._get_image(item[1])
        name = save_image(self.SOURCE, self.SOURCE_TYPE, image, date)
        return name

    @staticmethod
    def get_rating(item: str) -> int | None:
        try:
            return int(item)
        except ValueError:
            return None

    @staticmethod
    def get_volume(item: str) -> int | None:
        regex = re.search(TITLE_VOLUME_PATTERN_MATCH, item)
        volume = int(regex["volume"]) if regex else None
        return volume

    @staticmethod
    def get_release_date(item: str) -> datetime.date | None:
        regex = re.search(TITLE_DATE_PATERN_MATCH, item)
        try:
            date = (
                datetime.date(
                    int(regex["year"]), int(regex["month"]), int(regex["day"])
                )
                if regex
                else None
            )
        except ValueError:
            return None
        return date

    # ------------methods that can be invoked somewhere outside------------
    async def find_latest_date(
        self, date: datetime.date, action: str
    ) -> datetime.date | None:
        assert action in ("forward", "backward")
        main_page: BeautifulSoup = await self.fetch(
            self.MAIN_URL, commands=["content", "read"]
        )
        try:
            dates: list[BeautifulSoup] = main_page.find(
                "ul", {"class": "list_body"}
            ).find_all("li")
        except AttributeError as error:
            raise error
        date = (
            operator.add(date, datetime.timedelta(days=1))
            if action == "forward"
            else operator.sub(date, datetime.timedelta(days=1))
        )
        operator_action = operator.ge if action == "forward" else operator.le
        for i, row in enumerate(dates):
            guessed_date = convert_str_to_date(str(row.text), TITLE_DATE_PATERN_MATCH)
            if (
                operator_action(guessed_date, date)
                and convert_str_to_date(
                    str(dates[min(i + 1, len(dates) - 1)].text), TITLE_DATE_PATERN_MATCH
                )
                <= date
            ):
                return guessed_date
        return None
