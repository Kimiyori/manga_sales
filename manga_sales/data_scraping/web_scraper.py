from __future__ import annotations
import datetime
import asyncio
import re
import difflib
from typing import Callable
from aiohttp import ClientResponse
from .exceptions import BSError, ConnectError, NotFound
from manga_sales.data_scraping.meta import AbstractScraper
from manga_sales.data_scraping.dataclasses import Content
from bs4 import BeautifulSoup
import uuid


class OriconScraper(AbstractScraper):
    """
    Class for collecting data from Oricon
    """

    _URL: str = "https://www.oricon.co.jp/rank/obc/w/"
    _SEARCH_URL: str = "https://www.mangaupdates.com/series.html?search="
    _NUMBER_PAGES: int = 4

    def __init__(self) -> None:
        super().__init__()

    async def fetch(
        self, url: str, commands: list[str] | None = None, bs: bool = True
    ) -> BeautifulSoup | ClientResponse:
        """
        Method for fetching given url

        Args:
            url:url from which exctract data
            commands: set fo commands that will be applied to response
            bs: return bs4 or pure response
        """
        response = await self.session.fetch(url, commands=commands)
        return BeautifulSoup(response, "html.parser") if bs else response

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

    async def _get_title(self, item: BeautifulSoup) -> tuple[str, BeautifulSoup]:
        def get_most_similar_title(original_name: str, link: BeautifulSoup) -> str:

            items = link.find_all("div", {"class": "col-12 col-lg-6 p-3 text"})

            titles: dict[str, str] = {}

            for item in items:
                item = item.find("div", {"class": "text"})
                try:
                    titles[item.find("b").string] = item.find("a")["href"]
                except KeyError:
                    continue
            most_similar = difflib.get_close_matches(original_name, titles.keys())
            # return link to most similar if they exist
            # else return first in list fo titles
            return (
                titles[most_similar[0]]
                if most_similar
                else titles[list(titles.keys())[0]]
            )

        try:
            split_name = item.find("h2", {"class": "title"}).string.split(" ")
            japanese_name = (
                " ".join(x for x in split_name[:-1])
                if len(split_name) > 1
                else split_name[0]
            )
            # get list fo titles from mangaupdates
            # with search by japanese title
            mangau_list = await self.fetch(
                url=self._SEARCH_URL + japanese_name, commands=["content", "read"]
            )
            # find most similar title
            mangau_item_link = get_most_similar_title(japanese_name, mangau_list)
            title_page: BeautifulSoup = await self.fetch(
                url=mangau_item_link, commands=["content", "read"]
            )
            english_name: str = title_page.find(
                "span", {"class": "releasestitle tabletitle"}
            ).string
        except AttributeError:
            raise BSError("Can't parse to find title name")
        return english_name, title_page

    def _get_authors(self, item: BeautifulSoup) -> list[str]:
        try:
            authors_tag = item.find("b", string="Author(s)").parent.find_next_sibling(
                "div"
            )
            authors_list = [author.string for author in authors_tag.find_all("u")]
        except AttributeError:
            return []
        return authors_list

    def _get_publishers(self, item: BeautifulSoup) -> list[str]:
        try:
            publishers_tag = item.find(
                "b", string="Original Publisher"
            ).parent.find_next_sibling("div")
            publishers = [
                publisher.string for publisher in publishers_tag.find_all("u")
            ]
        except AttributeError:
            return []
        return publishers

    async def _get_image(
        self, item: BeautifulSoup
    ) -> tuple[str, ClientResponse] | tuple[None, None]:
        try:
            img_url = item.find("p", {"class": "image"}).find("img").get("src")
            if img_url is None:
                return None, None
        except AttributeError:
            return None, None
        reg = re.search(r".(\w+)$", img_url)
        extension = reg.group(1) if reg else "jpg"
        name = f"{uuid.uuid4()}.{extension}"
        try:
            binary_image = await self.fetch(img_url, ["read"], False)
        except ConnectError:
            return None, None
        return name, binary_image

    async def retrieve_data(self, url: str) -> None:
        data: BeautifulSoup = await self.fetch(url, commands=["content", "read"])
        list_items = data.find_all("section", {"class": "box-rank-entry"})
        if not list_items:
            raise BSError("Fail to find class with titles list")
        for item in list_items:
            rating: int = self._get_rating(item)
            image_name, image = await self._get_image(item)
            name, data_url = await self._get_title(item)
            authors = self._get_authors(data_url)
            publishers = self._get_publishers(data_url)
            volume = self._get_volume(item)
            release = self._get_release_date(item)
            sold = self._get_sold_amount(item)
            content = Content(
                name,
                volume,
                image_name,
                image,
                authors,
                publishers,
                release,
                rating,
                sold,
            )
            self.rating_list.append(content)

    async def get_data(self, date: str) -> list[Content]:
        self.rating_list = []
        pages: list[str] = [
            self._URL + date + f"/p/{x}/" for x in range(1, self._NUMBER_PAGES)
        ]
        async with self.session:
            tasks = [asyncio.create_task(self.retrieve_data(page)) for page in pages]
            await asyncio.gather(*tasks)

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
