import datetime
from unittest import mock
import pytest
from manga_scrapers.exceptions import BSError, NotFound
from manga_scrapers.scrapers.rating_scrapers.oricon_scraper import (
    OriconWeeklyScraper,
)
from manga_scrapers.scrapers.rating_scrapers.shoseki_scraper import (
    ShosekiWeeklyScraper,
)
from manga_scrapers.utils.url_handler import build_url, update_url
from manga_scrapers.test.conftest import (
    oricon_container,
    shoseki_container,
    oricon_item,
    oricon_list,
    manga_updates_title,
    manga_updates_list,
    shoseki_list,
    shoseki_weekly_list,
    shoseki_item,
    amazon,
    aioresponse,
    manga_updates_container,
    cdjapan_container,
)


class TestShosekiScraper:
    async def test_get_list_raw_data(
        self, aioresponse, shoseki_container, shoseki_weekly_list
    ):
        aioresponse.get(
            "url",
            status=200,
            body=str(shoseki_weekly_list),
        )
        list_items = await shoseki_container._get_list_raw_data("url")
        assert all(len(x) == 3 for x in list_items)
        assert len(list_items) == 30

    async def test_get_list_raw_data_wrong_class(
        self, aioresponse, shoseki_container, shoseki_weekly_list
    ):
        shoseki_weekly_list.find("div", {"class": "content"})["class"] = "test"
        aioresponse.get(
            "url",
            status=200,
            body=str(shoseki_weekly_list),
        )
        with pytest.raises(AttributeError):
            await shoseki_container._get_list_raw_data("url")

    def test_convert_str_to_date(self, shoseki_container):
        res = shoseki_container.convert_str_to_date("2022-11-11")
        assert res == datetime.date(2022, 11, 11)

    def test_convert_str_to_date_without_day(self, shoseki_container):
        res = shoseki_container.convert_str_to_date("2022-11")
        assert res == datetime.date(2022, 11, 1)

    def test_convert_str_to_date_error(self, shoseki_container):
        with pytest.raises(AssertionError):
            shoseki_container.convert_str_to_date("11-11-2022")

    async def test_get_data_url(self, aioresponse, shoseki_container, shoseki_list):
        aioresponse.get(
            shoseki_container.MAIN_URL,
            status=200,
            body=str(shoseki_list),
        )
        res = await shoseki_container._get_data_url("2022-10-04")
        assert res == "http://shosekiranking.blog.fc2.com/blog-entry-4115.html"

    async def test_get_data_url_wrong_class(
        self, aioresponse, shoseki_container, shoseki_list
    ):
        shoseki_list.find("ul", {"class": "list_body"})["class"] = "test"
        aioresponse.get(
            shoseki_container.MAIN_URL,
            status=200,
            body=str(shoseki_list),
        )
        with pytest.raises(AttributeError):
            await shoseki_container._get_data_url("2022-10-04")

    async def test_get_data_url_none1(
        self, aioresponse, shoseki_container, shoseki_list
    ):
        lst = shoseki_list.find("ul", {"class": "list_body"}).find_all("li")
        for x in lst:
            x.name = "test"
        aioresponse.get(
            shoseki_container.MAIN_URL,
            status=200,
            body=str(shoseki_list),
        )
        res = await shoseki_container._get_data_url("2022-10-04")
        assert res == None

    async def test_get_data_url_none2(
        self, aioresponse, shoseki_container, shoseki_list
    ):
        aioresponse.get(
            shoseki_container.MAIN_URL,
            status=200,
            body=str(shoseki_list),
        )
        res = await shoseki_container._get_data_url("2020-10-11")
        assert res == None

    async def test_get_original_title(self, shoseki_container):
        lst = [
            ["1", "9784088831275", "SPY×FAMILY 10 集英社 遠藤達哉 2022.10.4"],
            ["2", "9784065290538", "きのう何食べた? 20 講談社 よしながふみ 2022.10.21"],
            ["3", "9784088832715", "チェンソーマン 12 集英社 藤本タツキ 2022.10.4"],
        ]
        res = shoseki_container._get_original_title(lst[0][2])
        assert res == "SPY×FAMILY"
        res1 = shoseki_container._get_original_title(lst[1][2])
        assert res1 == "きのう何食べた?"
        res2 = shoseki_container._get_original_title(lst[2][2])
        assert res2 == "チェンソーマン"
        res3 = shoseki_container._get_original_title("怪獣８号　７ 集英社 松本直也 2022.7.4")
        assert res3 == "怪獣８号"

    @pytest.mark.asyncio
    @mock.patch(
        "manga_scrapers.scrapers.rating_scrapers.shoseki_scraper.save_image",
        return_value=None,
    )
    async def test_get_image(
        self, mock_img, cdjapan_container, shoseki_container, amazon, aioresponse
    ):
        aioresponse.get(
            "https://www.amazon.co.jp/s?i=stripbooks&ref=nb_sb_noss&k=111",
            status=200,
            body=str(amazon),
        )
        aioresponse.get(
            "https://m.media-amazon.com/images/I/61Hph+T004L._AC_UY218_.jpg",
            status=200,
            body=bytes("img", "utf-8"),
        )
        res = await shoseki_container._get_image("111")
        assert isinstance(res, bytes)

    def test_get_rating(self, shoseki_container):
        res = shoseki_container.get_rating("33")
        assert res == 33

    def test_get_rating_fail(self, shoseki_container):
        res = shoseki_container.get_rating("aa")
        assert res == None

    def test_get_volume(self, shoseki_container):
        res = shoseki_container.get_volume("SPY×FAMILY 10 集英社 遠藤達哉 2022.10.4")
        assert res == 10
        res1 = shoseki_container.get_volume("怪獣８号　７ 集英社 松本直也 2022.7.4")
        assert res1 == 7

    def test_get_volume_none(self, shoseki_container):
        res = shoseki_container.get_volume("SPY×FAMILY 集英社 遠藤達哉 2022.10.4")
        assert res == None
        res1 = shoseki_container.get_volume("怪獣８号 集英社 松本直也 2022.7.4")
        assert res1 == None

    def test_get_release_date(self, shoseki_container):
        res = shoseki_container.get_release_date("SPY×FAMILY 10 集英社 遠藤達哉 2022.10.4")
        assert res == datetime.date(2022, 10, 4)

    def test_get_release_date_none(self, shoseki_container):
        res = shoseki_container.get_release_date("SPY×FAMILY 10 集英社 遠藤達哉")
        assert res == None

    def test_get_release_date_value_error(self, shoseki_container):
        res = shoseki_container.get_release_date("SPY×FAMILY 10 集英社 遠藤達哉 4.10.2022")
        assert res == None

    @pytest.mark.asyncio
    async def test_find_latest_date(self, aioresponse, shoseki_container, shoseki_list):
        aioresponse.get(shoseki_container.MAIN_URL, status=200, body=str(shoseki_list))
        date = await shoseki_container.find_latest_date(
            datetime.date(2022, 10, 11), "forward"
        )
        assert date == datetime.date(2022, 10, 18)

    @pytest.mark.asyncio
    async def test_find_latest_date_first(
        self, aioresponse, shoseki_container, shoseki_list
    ):
        aioresponse.get(shoseki_container.MAIN_URL, status=200, body=str(shoseki_list))
        date = await shoseki_container.find_latest_date(
            datetime.date(2022, 11, 11), "backward"
        )
        assert date == datetime.date(2022, 11, 1)

    @pytest.mark.asyncio
    async def test_find_latest_date_none(
        self, aioresponse, shoseki_container, shoseki_list
    ):
        aioresponse.get(shoseki_container.MAIN_URL, status=200, body=str(shoseki_list))
        date = await shoseki_container.find_latest_date(
            datetime.date(2020, 11, 11), "forward"
        )
        assert date == None

    @pytest.mark.asyncio
    async def test_find_latest_date_exception(
        self, aioresponse, shoseki_container, shoseki_list
    ):
        shoseki_list.find("ul", {"class": "list_body"})["class"] = "wrong"
        aioresponse.get(shoseki_container.MAIN_URL, status=200, body=str(shoseki_list))
        with pytest.raises(AttributeError):
            await shoseki_container.find_latest_date(
                datetime.date(2022, 11, 11), "forward"
            )

    async def test_get_aux_data(
        self,
        aioresponse,
        shoseki_container,
        manga_updates_container,
        manga_updates_title,
        manga_updates_list,
    ):
        aioresponse.get(
            build_url(
                scheme="https",
                netloc="www.mangaupdates.com",
                path=["series.html"],
                query={"type": "manga", "perpage": 5, "search": "暁のARIA"},
            ),
            status=200,
            body=str(manga_updates_list),
        )
        aioresponse.get(
            "https://www.mangaupdates.com/series/yobj9va/aria",
            status=200,
            body=str(manga_updates_title),
        )
        name, authors, publishers = await shoseki_container._get_aux_data(
            "暁のARIA 10 集英社 遠藤達哉 2022.10.4"
        )
        assert authors == ["AKAISHI Michiyo"]
        assert publishers == ["Shogakukan"]
        assert name == "Akatsuki no Aria"
