from __future__ import annotations
import datetime
import re
import unicodedata
import uuid
from bs4 import BeautifulSoup
from src.data_scraping.aux_scrapers.abc import AuxDataParserAbstract
from src.data_scraping.dataclasses import Content
from src.data_scraping.exceptions import ConnectError, Unsuccessful
from src.data_scraping.services.images_service import save_image
from src.data_scraping.session_context_manager import Session
from .abc import MainDataAbstractScraper


class ShosekiWeeklyScraper(MainDataAbstractScraper):
    """
    Class for collecting data from Shoseki
    """

    SOURCE = "Shoseki"
    SOURCE_TYPE = "Weekly"
    MAIN_URL: str = "http://shosekiranking.blog.fc2.com/blog-category-6.html"

    def __init__(
        self, session: Session, main_info_parser: AuxDataParserAbstract
    ) -> None:
        self.main_info_parser = main_info_parser
        super().__init__(session)

    # ------------helper methods for main methods------------
    @staticmethod
    def convert_str_to_date(date: str) -> datetime.date:
        """Convert string date to datetime.date type

        Args:
            date (str): The method accepts the following date patterns:%Y(-/.)%m(-/.)%d,
            else throws error

        Returns:
            datetime.date: if day not passed, then it set default to 1
        """
        str_date = re.search(
            r"^(?P<year>[0-9]{4})[-\/\.](?P<month>[0-9]{1,2})[-\/\.]?(?P<day>[0-9]{0,2})",
            date,
        )
        assert str_date is not None, "Fail match date"
        return datetime.datetime.strptime(
            (
                f'{str_date["year"]}/'
                f'{str_date["month"]}/'
                f'{str_date["day"] if str_date["day"] else 1}'
            ),
            "%Y/%m/%d",
        ).date()

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

    async def _get_aux_data(self, item: str) -> tuple[str, list[str], list[str]]:
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
        self, index: int, row: list[str], date: str
    ) -> Content:
        rating = self.get_rating(row[0])
        name, authors, publishers = await self._get_aux_data(row[2])
        image = await self.get_image(row[1], date)
        content = Content(
            name=name,
            volume=self.get_volume(row[2]),
            image=image,
            authors=authors,
            publishers=publishers,
            release_date=self.get_release_date(row[2]),
            rating=rating if rating else index,
        )
        return content

    async def _retrieve_data(self, url: str, date: str) -> list[Content]:
        list_items = await self._get_list_raw_data(url)
        lst = []
        for i, row in enumerate(list_items):
            content = await self.create_content_item(i, row, date)
            lst.append(content)
        return lst

    async def _get_data_url(self, date: str) -> str | None:
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
                r"^([0-9]+)\/([0-9]+)\/([0-9]+)\s:\s.+",
                r"\g<1>-\g<2>-\g<3>",
                date_obj.text,
            )
            if date == guess_date:
                url: str = date_obj.find("a")["href"]
                return url
        return None

    @staticmethod
    def _get_original_title(item: str) -> str:
        reg = re.search(r"^(\S+|\D+)\s\d+", item)
        assert reg is not None
        japanese_name = reg.group(1)
        return japanese_name

    # ------------main methods for collecting gata that invokes inside class------------
    async def get_data(self, date: str) -> list[Content] | None:
        url = await self._get_data_url(date)
        rating_list = await self._retrieve_data(url, date) if url else None
        return rating_list

    async def get_image(self, item: str, date: str) -> str | None:
        def create_name(url: str) -> str:
            reg = re.search(r".(\w+)$", url)
            extension = reg.group(1) if reg else "jpg"
            name = f"{uuid.uuid4()}.{extension}"
            return name

        amazon_url = f"https://www.amazon.co.jp/s?i=stripbooks&ref=nb_sb_noss&k={item}"
        page_image: BeautifulSoup = await self.fetch(
            amazon_url, commands=["content", "read"]
        )
        try:
            img_url = page_image.find("img", {"class": "s-image"})["src"]
            name = create_name(img_url)
            image_file = await self.fetch(img_url, ["read"], False)
        except (ConnectError, Unsuccessful, AttributeError, TypeError):
            return None
        assert isinstance(image_file, bytes)
        save_image(self.SOURCE, self.SOURCE_TYPE, image_file, name, date)
        return name

    def get_rating(self, item: str) -> int | None:
        try:
            return int(item)
        except ValueError:
            return None

    def get_volume(self, item: str) -> int | None:
        regex = re.search(r"^[\S]+\s(\d+)\s\D+", item)
        if regex:
            volume = int(regex.group(1))
            return volume
        return None

    def get_release_date(self, item: str) -> datetime.date | None:
        regex = re.search(r"(?P<year>[\d]+).(?P<month>[\d]+).(?P<day>[\d]+)$", item)
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
        self, date: datetime.date, date_convert: bool = True
    ) -> datetime.date | str | None:
        main_page: BeautifulSoup = await self.fetch(
            self.MAIN_URL, commands=["content", "read"]
        )
        try:
            dates: list[BeautifulSoup] = main_page.find(
                "ul", {"class": "list_body"}
            ).find_all("li")
        except AttributeError as error:
            raise error
        date -= datetime.timedelta(days=1)
        for i, row in enumerate(dates):
            guessed_date = self.convert_str_to_date(str(row.text))
            if guessed_date <= date:
                return guessed_date if date_convert else dates[i].text
        return None
