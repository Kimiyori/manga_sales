from __future__ import annotations
import datetime
import asyncio
import re
from typing import Callable
import unicodedata
from .exceptions import BSError, ConnectError, NotFound
from manga_sales.data_scraping.meta import AbstractScraper, MangaUpdatesAbstract
from manga_sales.data_scraping.dataclasses import Content
from bs4 import BeautifulSoup
import uuid


class OriconWeeklyScraper(MangaUpdatesAbstract, AbstractScraper):
    """
    Class for collecting data from Oricon
    """

    _URL: str = "https://www.oricon.co.jp/rank/obc/w/"
    _NUMBER_PAGES: int = 4

    def _get_rating(self, item: BeautifulSoup) -> int:
        try:
            rating = int(item.find("p", {"class": "num"}).text)
        except (AttributeError, ValueError):
            return 0
        return rating

    def _get_volume(self, item: BeautifulSoup) -> int | None:
        volume = None
        try:
            list = item.find("h2", {"class": "title"}).string.split(" ")
        except AttributeError:
            return volume
        # iterate over all space-separated words from the title and
        # catch the first integer (usually this will be the volume)
        for item in list:
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
            split_name = item.find("h2", {"class": "title"}).string.split(" ")
            japanese_name = (
                " ".join(x for x in split_name[:-1])
                if len(split_name) > 1
                else split_name[0]
            )
        except AttributeError:
            raise BSError("Can't parse to find title name")
        return japanese_name

    async def _get_image(self, item: BeautifulSoup) -> str | None:
        try:
            img_url = item.find("p", {"class": "image"}).find("img").get("src")
            if img_url is None:
                return None
            reg = re.search(r".(\w+)$", img_url)
            extension = reg.group(1) if reg else "jpg"
            name = f"{uuid.uuid4()}.{extension}"
            image_file = await self.fetch(img_url, ["read"], False)
            self.save_image(image_file, name)
        except (ConnectError, AttributeError):
            return None
        return name

    async def retrieve_data(self, url: str) -> None:
        data: BeautifulSoup = await self.fetch(url, commands=["content", "read"])
        list_items = data.find_all("section", {"class": "box-rank-entry"})
        if not list_items:
            raise BSError("Fail to find class with titles list")
        for item in list_items:
            rating = self._get_rating(item)
            image = await self._get_image(item)
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
            self.rating_list.append(content)

    async def get_data(self, date: str) -> list[Content]:
        self.date = date
        self.rating_list = []
        pages: list[str] = [
            self._URL + date + f"/p/{x}/" for x in range(1, self._NUMBER_PAGES)
        ]
        async with self.session:
            tasks = [asyncio.create_task(self.retrieve_data(page)) for page in pages]
            self.rating_list = await asyncio.gather(*tasks)
        return self.rating_list

    async def find_latest_date(
        self,
        date: datetime.date,
        operator: Callable[[datetime.date, datetime.timedelta], datetime.date],
    ) -> datetime.date | None:
        async with self.session:
            count_days = 1
            while count_days <= 7:
                guess_date = operator(date, datetime.timedelta(days=count_days))
                url = self._URL + guess_date.strftime("%Y-%m-%d") + "/"
                try:
                    await self.fetch(url, bs=False)
                except NotFound:
                    count_days += 1
                    continue
                return guess_date
        return None


class ShosekiWeeklyScraper(MangaUpdatesAbstract, AbstractScraper):
    """
    Class for collecting data from Shoseki
    """

    _URL: str = "http://shosekiranking.blog.fc2.com/blog-category-6.html"

    async def get_data(self, date: str) -> list[Content]:
        self.date = date
        self.rating_list = []
        url = None
        async with self.session:
            main_page: BeautifulSoup = await self.fetch(
                self._URL, commands=["content", "read"]
            )
            dates: list[BeautifulSoup] = main_page.find(
                "ul", {"class": "list_body"}
            ).find_all("li")
            for date_obj in dates:
                guess_date: str = re.sub(
                    r"^([0-9]+)\/([0-9]+)\/([0-9]+) : .+",
                    r"\g<1>-\g<2>-\g<3>",
                    date_obj.text,
                )
                if date == guess_date:
                    url: str = date_obj.find("a")["href"]
                    break
            await self.retrieve_data(url) if url else None
        return self.rating_list

    async def retrieve_data(self, url: str) -> None:
        page: BeautifulSoup = await self.fetch(url, commands=["content", "read"])
        body = page.find("div", {"class": "entry_body"})
        text_items: str = body.get_text(strip=True, separator="\n").splitlines()
        list_items: list[list[str]] = [text_items[i : i + 3] for i in range(0, 90, 3)]
        urls: list[str] = body.find_all("a")
        for i in range(len(list_items)):
            list_items[i].append(urls[i]["href"])
            list_items[i][2] = unicodedata.normalize("NFKC", list_items[i][2])
        for row in list_items:
            rating: int = self._get_rating(row[0])
            volume: int = self._get_volume(row[2])
            name, data_url = await self._get_title(row[2])
            authors = self._get_authors(data_url)
            publishers = self._get_publishers(data_url)
            sold = self._get_sold_amount()
            release = self._get_release_date(row[2])
            image = await self._get_image(row[3])
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
            self.rating_list.append(content)

    async def _get_image(self, url):
        page_image = await self.fetch(url, commands=["content", "read"])
        img_url = page_image.find("img", {"class": "s-image"})["src"]
        reg = re.search(r".(\w+)$", img_url)
        extension = reg.group(1) if reg else "jpg"
        name = f"{uuid.uuid4()}.{extension}"
        try:
            image_file = await self.fetch(img_url, ["read"], False)
            self.save_image(image_file, name)
        except ConnectError:
            return None
        return name

    def _get_rating(self, item: str) -> int:
        return int(item)

    def _get_volume(self, item: str) -> int | None:
        regex = re.search(r"^\D+ (\d+)\D+", item).group(1)
        return int(regex)

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

    def _get_sold_amount(self) -> None:
        return None

    def _get_original_title(self, item: str) -> str:
        japanese_name: str = re.search(r"^(\D+)", item).group(1)
        return japanese_name

    async def find_latest_date(
        self,
        date: datetime.date,
        operator: Callable[[datetime.date, datetime.timedelta], datetime.date],
    ) -> datetime.date | None:
        return await super().find_latest_date(date, operator)
