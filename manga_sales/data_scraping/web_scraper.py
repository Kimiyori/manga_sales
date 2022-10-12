from __future__ import annotations
from abc import abstractmethod
import datetime
import asyncio
import difflib
import re
import unicodedata
import uuid
from bs4 import BeautifulSoup
from manga_sales.data_scraping.meta import (
    ChartItemDataParserAbstract,
    MainItemDataParserAbstract,
)
from manga_sales.data_scraping.dataclasses import Content
from manga_sales.data_scraping.exceptions import BSError, ConnectError, NotFound


class MangaUpdatesParser(MainItemDataParserAbstract):
    _MAIN_URL: str = "https://www.mangaupdates.com/series.html?search="

    async def get_main_info_page(self, title: str) -> BeautifulSoup:
        filter_list = await self.fetch(
            url=self._MAIN_URL + title, commands=["content", "read"]
        )
        # find most similar title
        most_similar_title = self._get_most_similar_title(title, filter_list)
        title_page: BeautifulSoup = await self.fetch(
            url=most_similar_title, commands=["content", "read"]
        )
        return title_page

    @staticmethod
    def _get_most_similar_title(original_name: str, link: BeautifulSoup) -> str:

        items = link.find_all("div", {"class": "col-12 col-lg-6 p-3 text"})
        assert items is not None
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
            titles[most_similar[0]] if most_similar else titles[list(titles.keys())[0]]
        )

    @staticmethod
    def get_authors(page: BeautifulSoup) -> list[str]:
        try:
            authors_tag = page.find("b", string="Author(s)").parent.find_next_sibling(
                "div"
            )
            authors_list = [author.string for author in authors_tag.find_all("u")]
        except AttributeError:
            return []
        return authors_list

    @staticmethod
    def get_publishers(page: BeautifulSoup) -> list[str]:
        try:
            publishers_tag = page.find(
                "b", string="Original Publisher"
            ).parent.find_next_sibling("div")
            publishers = [
                publisher.string for publisher in publishers_tag.find_all("u")
            ]
        except AttributeError:
            return []
        return publishers

    @abstractmethod
    def _get_original_title(self, item: BeautifulSoup | str) -> str:
        pass

    async def get_title(self, page: BeautifulSoup) -> tuple[str, BeautifulSoup]:
        original_name = self._get_original_title(page)
        title_page: BeautifulSoup = await self.get_main_info_page(original_name)
        english_name: str = title_page.find(
            "span", {"class": "releasestitle tabletitle"}
        ).string
        return english_name, title_page


class OriconWeeklyScraper(ChartItemDataParserAbstract, MangaUpdatesParser):
    """
    Class for collecting data from Oricon
    """

    _CHART_URL: str = "https://www.oricon.co.jp/rank/obc/w/"
    _NUMBER_PAGES: int = 4

    def get_rating(self, item: BeautifulSoup) -> int:
        try:
            rating = int(item.find("p", {"class": "num"}).text)
        except (AttributeError, ValueError) as error:
            raise error
        return rating

    def get_volume(self, item: BeautifulSoup) -> int | None:
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

    def get_sale(self, item: BeautifulSoup) -> int:
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

    async def get_image(self, item: BeautifulSoup, date: str) -> str | None:
        try:
            img_url = item.find("p", {"class": "image"}).find("img").get("src")
            if img_url is None:
                return None
            reg = re.search(r".(\w+)$", img_url)
            extension = reg.group(1) if reg else "jpg"
            name = f"{uuid.uuid4()}.{extension}"
            image_file = await self.fetch(img_url, ["read"], False)
            assert isinstance(image_file, bytes)
            self.save_image("oricon", "weekly", image_file, name, date)
        except (ConnectError, AttributeError):
            return None
        return name

    async def _get_list_raw_data(self, url: str) -> BeautifulSoup:
        data: BeautifulSoup = await self.fetch(url, commands=["content", "read"])
        list_items = data.find_all("section", {"class": "box-rank-entry"})
        if not list_items:
            raise BSError("Fail to find class with titles list")
        return list_items

    async def _retrieve_data(self, url: str, date: str) -> list[Content]:
        list_items = await self._get_list_raw_data(url)
        lst = []
        for item in list_items:
            rating = self.get_rating(item)
            image = await self.get_image(item, date)
            name, data_url = await self.get_title(item)
            authors = self.get_authors(data_url)
            publishers = self.get_publishers(data_url)
            volume = self.get_volume(item)
            release = self.get_release_date(item)
            sold = self.get_sale(item)
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
        pages: list[str] = [
            self._CHART_URL + date + f"/p/{x}/" for x in range(1, self._NUMBER_PAGES)
        ]
        async with self.session:
            tasks = [
                asyncio.create_task(self._retrieve_data(page, date)) for page in pages
            ]
            rating_list = await asyncio.gather(*tasks)
        return rating_list

    async def find_latest_date(
        self, date: datetime.date, date_convert: bool = True
    ) -> datetime.date | None:
        async with self.session:
            count_days = 1
            while count_days <= 7:
                guess_date = date + datetime.timedelta(days=count_days)
                url = self._CHART_URL + guess_date.strftime("%Y-%m-%d") + "/"
                try:
                    await self.fetch(url, return_bs=False)
                except NotFound:
                    count_days += 1
                    continue
                return guess_date if date_convert else guess_date
        return None


class ShosekiWeeklyScraper(ChartItemDataParserAbstract, MangaUpdatesParser):
    """
    Class for collecting data from Shoseki
    """

    _CHART_URL: str = "http://shosekiranking.blog.fc2.com/blog-category-6.html"

    async def _get_list_raw_data(self, url: str) -> BeautifulSoup:
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
        list_items = await self._get_list_raw_data(url)
        lst = []
        for row in list_items:
            rating = self.get_rating(row[0])
            volume = self.get_volume(row[2])
            name, data_url = await self.get_title(row[2])
            authors = self.get_authors(data_url)
            publishers = self.get_publishers(data_url)
            release = self.get_release_date(row[2])
            image = await self.get_image(row[1], date)
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
            self._CHART_URL, commands=["content", "read"]
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
            rating_list = await self._retrieve_data(url, date) if url else None
        return rating_list

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
                self._CHART_URL, commands=["content", "read"]
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

    async def get_image(self, item: str, date: str) -> str | None:
        amazon_url = f"https://www.amazon.co.jp/s?i=stripbooks&ref=nb_sb_noss&k={item}"
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
            self.save_image("shoseki", "weekly", image_file, name, date)
        except ConnectError:
            return None
        return name

    def get_rating(self, item: str) -> int:
        try:
            return int(item)
        except ValueError as error:
            raise error

    def get_volume(self, item: str) -> int | None:
        regex = re.search(r"^\D+ (\d+) \D+", item)
        assert regex is not None
        try:
            volume = int(regex.group(1))
            return volume
        except ValueError:
            pass
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

    def get_sale(self, item: str) -> None:
        return None

    @staticmethod
    def _get_original_title(item: str) -> str:
        reg = re.search(r"^(\D+)", item)
        assert reg is not None
        japanese_name = reg.group(1)
        return japanese_name
