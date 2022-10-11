from __future__ import annotations
import datetime
import asyncio
import re
import unicodedata
import uuid
from bs4 import BeautifulSoup
from manga_sales.data_scraping.meta import AbstractScraper, MangaUpdatesAbstract
from manga_sales.data_scraping.dataclasses import Content
from manga_sales.data_scraping.exceptions import BSError, ConnectError, NotFound


class OriconWeeklyScraper(MangaUpdatesAbstract, AbstractScraper):
    """
    Class for collecting data from Oricon
    """

    _URL: str = "https://www.oricon.co.jp/rank/obc/w/"
    _NUMBER_PAGES: int = 4

    def _get_rating(self, item: BeautifulSoup) -> int:
        try:
            rating = int(item.find("p", {"class": "num"}).text)
        except (AttributeError, ValueError) as error:
            raise error
        return rating

    def _get_volume(self, item: BeautifulSoup) -> int | None:
        volume = None
        try:
            lst = item.find("h2", {"class": "title"}).string.split(" ")
        except AttributeError:
            return volume
        # iterate over all space-separated words from the title and
        # catch the first integer (usually this will be the volume)
        for item in lst:
            try:
                volume = int(item)
                break
            except ValueError:
                continue
        return volume

    def _get_release_date(self, item: BeautifulSoup) -> datetime.date | None:
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

    def _get_sold_amount(self, item: BeautifulSoup) -> int:
        try:
            text = (
                item.find("ul", {"class": "list"})
                .find(lambda tag: tag.name == "li" and "推定売上部数" in tag.string)
                .string
            )
        except AttributeError:
            return 0
        regex_date = re.search(r"(?P<sold>[0-9,]+(?=部))", text)
        try:
            sold = int(regex_date["sold"].replace(",", "")) if regex_date else 0
        except ValueError:
            return 0
        return sold

    def _get_original_title(self, item: BeautifulSoup) -> str:

        try:
            split_name: list[str] = item.find("h2", {"class": "title"}).string.split(
                " "
            )
            japanese_name = (
                " ".join(x for x in split_name[:-1])
                if len(split_name) > 1
                else split_name[0]
            )
        except AttributeError:
            raise BSError("Can't parse to find title name") from AttributeError
        return japanese_name

    async def _get_image(self, item: BeautifulSoup, date: str) -> str | None:
        try:
            img_url = item.find("p", {"class": "image"}).find("img").get("src")
            if img_url is None:
                return None
            reg = re.search(r".(\w+)$", img_url)
            extension = reg.group(1) if reg else "jpg"
            name = f"{uuid.uuid4()}.{extension}"
            image_file = await self.fetch(img_url, ["read"], False)
            assert isinstance(image_file, bytes)
            self.save_image(image_file, name, date)
        except (ConnectError, AttributeError):
            return None
        return name

    async def get_list_raw_data(self, url: str) -> BeautifulSoup:
        data: BeautifulSoup = await self.fetch(url, commands=["content", "read"])
        list_items = data.find_all("section", {"class": "box-rank-entry"})
        if not list_items:
            raise BSError("Fail to find class with titles list")
        return list_items

    async def _retrieve_data(self, url: str, date: str) -> list[Content]:
        list_items = await self.get_list_raw_data(url)
        lst = []
        for item in list_items:
            rating = self._get_rating(item)
            image = await self._get_image(item, date)
            name, data_url = await self._get_title(item)
            authors = self._get_authors(data_url)
            publishers = self._get_publishers(data_url)
            volume = self._get_volume(item)
            release = self._get_release_date(item)
            sold = self._get_sold_amount(item)
            content = Content(
                name,
                volume,
                image,
                authors,
                publishers,
                release,
                rating,
                sold,
            )
            lst.append(content)
        return lst

    async def get_data(self, date: str) -> list[Content]:
        self.rating_list = []
        pages: list[str] = [
            self._URL + date + f"/p/{x}/" for x in range(1, self._NUMBER_PAGES)
        ]
        async with self.session:
            tasks = [
                asyncio.create_task(self._retrieve_data(page, date)) for page in pages
            ]
            self.rating_list = await asyncio.gather(*tasks)
        return self.rating_list

    async def find_latest_date(
        self, date: datetime.date, date_convert: bool = True
    ) -> datetime.date | None:
        async with self.session:
            count_days = 1
            while count_days <= 7:
                guess_date = date + datetime.timedelta(days=count_days)
                url = self._URL + guess_date.strftime("%Y-%m-%d") + "/"
                try:
                    await self.fetch(url, return_bs=False)
                except NotFound:
                    count_days += 1
                    continue
                return guess_date if date_convert else guess_date
        return None


class ShosekiWeeklyScraper(MangaUpdatesAbstract, AbstractScraper):
    """
    Class for collecting data from Shoseki
    """

    _URL: str = "http://shosekiranking.blog.fc2.com/blog-category-6.html"

    async def get_list_raw_data(self, url: str) -> BeautifulSoup:
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

    async def _retrieve_data(self, url: str, date: str) -> list[Content]:
        list_items = await self.get_list_raw_data(url)
        lst = []
        for row in list_items:
            rating = self._get_rating(row[0])
            volume = self._get_volume(row[2])
            name, data_url = await self._get_title(row[2])
            authors = self._get_authors(data_url)
            publishers = self._get_publishers(data_url)
            release = self._get_release_date(row[2])
            image = await self._get_image(row[1], date)
            content = Content(
                name=name,
                volume=volume,
                image=image,
                authors=authors,
                publisher=publishers,
                release_date=release,
                rating=rating,
                sold=None,
            )
            lst.append(content)
        return lst

    async def _get_data_url(self, date: str) -> str | None:
        main_page: BeautifulSoup = await self.fetch(
            self._URL, commands=["content", "read"]
        )
        try:
            dates: list[BeautifulSoup] = main_page.find(
                "ul", {"class": "list_body"}
            ).find_all("li")
        except AttributeError as error:
            raise error
        for date_obj in dates:
            guess_date: str = re.sub(
                r"^([0-9]+)\/([0-9]+)\/([0-9]+) : .+",
                r"\g<1>-\g<2>-\g<3>",
                date_obj.text,
            )
            if date == guess_date:
                url: str = date_obj.find("a")["href"]
                return url
        return None

    async def get_data(self, date: str) -> list[Content] | None:
        async with self.session:
            url = await self._get_data_url(date)
            self.rating_list = await self._retrieve_data(url, date) if url else None
        return self.rating_list

    @staticmethod
    def convert_str_to_date(date: str) -> datetime.datetime:
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
        )

    async def find_latest_date(
        self, date: datetime.date, date_convert: bool = True
    ) -> datetime.date | None:
        async with self.session:
            main_page: BeautifulSoup = await self.fetch(
                self._URL, commands=["content", "read"]
            )
            try:
                dates: list[BeautifulSoup] = main_page.find(
                    "ul", {"class": "list_body"}
                ).find_all("li")
            except AttributeError as error:
                raise error
            for i, row in enumerate(dates):
                guessed_date = self.convert_str_to_date(str(row.text))
                if guessed_date <= date:
                    return (
                        (
                            self.convert_str_to_date(str(dates[i - 1].text))
                            if date_convert
                            else dates[i - 1].text
                        )
                        if i > 0
                        else None
                    )
        return None

    async def _get_image(self, code: str, date: str) -> str | None:
        amazon_url = f"https://www.amazon.co.jp/s?i=stripbooks&ref=nb_sb_noss&k={code}"
        page_image: BeautifulSoup = await self.fetch(
            amazon_url, commands=["content", "read"]
        )
        img_url = page_image.find("img", {"class": "s-image"})["src"]
        reg = re.search(r".(\w+)$", img_url)
        extension = reg.group(1) if reg else "jpg"
        name = f"{uuid.uuid4()}.{extension}"
        try:
            image_file = await self.fetch(img_url, ["read"], False)
            assert isinstance(image_file, bytes)
            self.save_image(image_file, name, date)
        except ConnectError:
            return None
        return name

    def _get_rating(self, item: str) -> int:
        try:
            return int(item)
        except ValueError as error:
            raise error

    def _get_volume(self, item: str) -> int | None:
        regex = re.search(r"^\D+ (\d+) \D+", item)
        assert regex is not None
        try:
            volume = int(regex.group(1))
            return volume
        except ValueError:
            pass
        return None

    def _get_release_date(self, item: str) -> datetime.date | None:
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

    def _get_sold_amount(self, item: str) -> None:
        return

    def _get_original_title(self, item: str) -> str:
        reg = re.search(r"^(\D+)", item)
        assert reg is not None
        japanese_name = reg.group(1)
        return japanese_name
