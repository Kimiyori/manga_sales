import datetime
from unittest import mock
import pytest
from src.data_scraping.exceptions import BSError, NotFound
from src.data_scraping.main_scrapers.oricon_scraper import OriconWeeklyScraper
from src.data_scraping.main_scrapers.shoseki_scraper import ShosekiWeeklyScraper
from .conftest import (
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
)


class TestOriconScraper:
    def test_get_original_title_success(self, oricon_container, oricon_item):
        original_title = oricon_container._get_original_title(oricon_item)
        assert original_title == "SPY×FAMILY"

    def test_get_original_title_success_without_volume(
        self, oricon_container, oricon_item
    ):
        oricon_item.find("h2", {"class": "title"}).string = "SPY×FAMILY"
        original_title = oricon_container._get_original_title(oricon_item)
        assert original_title == "SPY×FAMILY"

    def test_get_original_title_empty_name(self, oricon_container, oricon_item):
        oricon_item.find("h2", {"class": "title"}).string = ""
        with pytest.raises(BSError):
            oricon_container._get_original_title(oricon_item)

    def test_get_original_title_wrong_class(self, oricon_container, oricon_item):
        oricon_item.find("h2", {"class": "title"})["class"] = "wrong_class"
        with pytest.raises(BSError):
            oricon_container._get_original_title(oricon_item)

    @pytest.mark.asyncio
    @mock.patch("src.data_scraping.meta.AbstractBase.fetch")
    async def test_get_list_raw_data_success(self, mock, oricon_container, oricon_list):
        mock.side_effect = [oricon_list]
        lst = await oricon_container._get_list_raw_data("2022-11=11")
        assert len(lst) == 10

    @pytest.mark.asyncio
    @mock.patch("src.data_scraping.meta.AbstractBase.fetch")
    async def test_get_list_raw_data_error(self, mock, oricon_container, oricon_list):
        lst = oricon_list.find_all("section", {"class": "box-rank-entry"})
        for x in lst:
            x["class"] = "something"
        mock.side_effect = [oricon_list]
        with pytest.raises(BSError):
            await oricon_container._get_list_raw_data("2022-11=11")

    def test_get_rating(self, oricon_container, oricon_item):
        rating = oricon_container.get_rating(oricon_item)
        assert rating == 1

    def test_get_rating_exception(self, oricon_container, oricon_item):
        oricon_item.find("p", {"class": "num"}).string = "f"
        rating = oricon_container.get_rating(oricon_item)
        assert rating == None

    def test_get_volume_without_volume(self, oricon_container, oricon_item):
        oricon_item.find("h2", {"class": "title"}).string = "SPY×FAMILY"
        rating = oricon_container.get_volume(oricon_item)
        assert rating == None

    def test_get_volume_wrong_class(self, oricon_container, oricon_item):
        oricon_item.find("h2", {"class": "title"})["class"] = "wrong"
        rating = oricon_container.get_volume(oricon_item)
        assert rating == None

    def test_get_release_date(self, oricon_container, oricon_item):
        date = oricon_container.get_release_date(oricon_item)
        assert date == datetime.date(2022, 10, 1)

    def test_get_release_date_wrong_class(self, oricon_container, oricon_item):
        oricon_item.find("ul", {"class": "list"})["class"] = "test"
        date = oricon_container.get_release_date(oricon_item)
        assert date == None

    def test_get_release_date_incorrect_text(self, oricon_container, oricon_item):
        oricon_item.find("ul", {"class": "list"}).find(
            lambda tag: tag.name == "li" and "発売日" in tag.string
        ).string = "発売日：2022$10!"
        date = oricon_container.get_release_date(oricon_item)
        assert date == None

    def test_get_sales(self, oricon_container, oricon_item):
        sales = oricon_container.get_sales(oricon_item)
        assert sales == 121_722

    def test_get_sales_wrong_class(self, oricon_container, oricon_item):
        oricon_item.find("ul", {"class": "list"})["class"] = "wrong"
        sales = oricon_container.get_sales(oricon_item)
        assert sales == None

    def test_get_sales_wrong_class(self, oricon_container, oricon_item):
        oricon_item.find("ul", {"class": "list"})["class"] = "wrong"
        sales = oricon_container.get_sales(oricon_item)
        assert sales == None

    @pytest.mark.asyncio
    @mock.patch(
        "src.data_scraping.main_scrapers.oricon_scraper.save_image", return_value=None
    )
    @mock.patch(
        "src.data_scraping.meta.AbstractBase.fetch", return_value=bytes("img", "utf-8")
    )
    async def test_get_image(self, mock, mock_img, oricon_container, oricon_item):
        img_name = await oricon_container.get_image(oricon_item, "date")
        assert isinstance(img_name, str)

    @pytest.mark.asyncio
    @mock.patch(
        "src.data_scraping.meta.AbstractBase.fetch", return_value="not bytes type"
    )
    async def test_get_image_wrong_img_type(
        self, mock_img, oricon_container, oricon_item
    ):
        with pytest.raises(AssertionError):
            await oricon_container.get_image(oricon_item, "date")

    @pytest.mark.asyncio
    async def test_get_image_wrong_class(self, oricon_container, oricon_item):
        oricon_item.find("p", {"class": "image"})["class"] = "not img"
        img_name = await oricon_container.get_image(oricon_item, "date")
        assert img_name == None

    @pytest.mark.asyncio
    @mock.patch(
        "src.data_scraping.meta.AbstractBase.fetch",
        side_effect=[NotFound, NotFound, "bingo"],
    )
    async def test_find_latest_date(self, mock, oricon_container):
        date = await oricon_container.find_latest_date(
            datetime.date(2022, 10, 11), "forward"
        )
        assert date == datetime.date(2022, 10, 14)

    @pytest.mark.asyncio
    @mock.patch("src.data_scraping.meta.AbstractBase.fetch", side_effect=[NotFound] * 9)
    async def test_find_latest_date_none(self, mock, oricon_container):
        date = await oricon_container.find_latest_date(
            datetime.date(2022, 10, 11), "forward"
        )
        assert date == None

    @mock.patch("src.data_scraping.meta.AbstractBase.fetch")
    async def test_get_aux_data(
        self,
        mock,
        oricon_container,
        oricon_item,
        manga_updates_title,
        manga_updates_list,
    ):
        mock.side_effect = [manga_updates_list, manga_updates_title]
        oricon_item.find("h2", {"class": "title"}).string = "暁のARIA"
        name, authors, publishers = await oricon_container._get_aux_data(oricon_item)
        assert authors == ["AKAISHI Michiyo"]
        assert publishers == ["Shogakukan"]
        assert name == "Akatsuki no Aria"

    @mock.patch("src.data_scraping.meta.AbstractBase.fetch")
    async def test_get_aux_data_exception(
        self,
        mock,
        oricon_container,
        oricon_item,
        manga_updates_title,
        manga_updates_list,
    ):
        lst = manga_updates_list.find_all("div", {"class": "col-12 col-lg-6 p-3 text"})
        for x in lst:
            x["class"] = "something"
        mock.side_effect = [manga_updates_list, manga_updates_title]
        oricon_item.find("h2", {"class": "title"}).string = "暁のARIA"
        name, authors, publishers = await oricon_container._get_aux_data(oricon_item)
        assert authors == []
        assert publishers == []
        assert name == "暁のARIA"

    @mock.patch(
        "src.data_scraping.main_scrapers.oricon_scraper.save_image", return_value=None
    )
    @mock.patch(
        "src.data_scraping.aux_scrapers.manga_updates_scraper.MangaUpdatesParser.fetch"
    )
    async def test_retrieve_data(
        self,
        mock_mangaupdates,
        mock_img,
        oricon_container,
        oricon_list,
        manga_updates_list,
        manga_updates_title,
    ):
        list_items = oricon_list.find_all("section", {"class": "box-rank-entry"})
        for x in list_items:
            x.find("h2", {"class": "title"}).string = "暁のARIA"
        mock_mangaupdates.side_effect = [manga_updates_list, manga_updates_title] * 10
        with mock.patch.object(
            OriconWeeklyScraper,
            "fetch",
            side_effect=[oricon_list] + [bytes("img", "utf-8")] * 30,
        ):
            res = await oricon_container._retrieve_data("url", "date")
            assert len(res) == 10
            for i, x in enumerate(res, start=1):
                assert x.rating == i
                assert x.name == "Akatsuki no Aria"

    @mock.patch(
        "src.data_scraping.main_scrapers.oricon_scraper.save_image", return_value=None
    )
    @mock.patch(
        "src.data_scraping.aux_scrapers.manga_updates_scraper.MangaUpdatesParser.fetch"
    )
    async def test_get_data(
        self,
        mock_mangaupdates,
        mock_img,
        oricon_container,
        oricon_list,
        manga_updates_list,
        manga_updates_title,
    ):
        list_items = oricon_list.find_all("section", {"class": "box-rank-entry"})
        for x in list_items:
            x.find("h2", {"class": "title"}).string = "暁のARIA"
        mock_mangaupdates.side_effect = [manga_updates_list, manga_updates_title] * 30
        with mock.patch.object(
            OriconWeeklyScraper,
            "fetch",
            side_effect=([oricon_list] + [bytes("img", "utf-8")] * 10) * 3,
        ):
            res = await oricon_container.get_data("date")
            assert len(res) == 30
            for i, x in enumerate(res, start=1):
                if i % 10 == 0:
                    i = 10
                else:
                    i %= 10
                assert x.rating == i
                assert x.name == "Akatsuki no Aria"


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
        "src.data_scraping.main_scrapers.shoseki_scraper.save_image", return_value=None
    )
    async def test_get_image(self, mock_img, shoseki_container, amazon, aioresponse):
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
        res = await shoseki_container.get_image("111", "date")
        assert isinstance(res, str)

    @pytest.mark.asyncio
    async def test_get_image_wrong_class(self, shoseki_container, amazon, aioresponse):
        amazon.find("img", {"class": "s-image"})["class"] = "test"
        aioresponse.get(
            "https://www.amazon.co.jp/s?i=stripbooks&ref=nb_sb_noss&k=url",
            status=200,
            body=str(amazon),
        )
        res = await shoseki_container.get_image("url", "date")
        assert res == None

    @pytest.mark.asyncio
    @mock.patch("asyncio.sleep", return_value=1)
    async def test_get_image_connect_fail(
        self, mock_sleep, shoseki_container, amazon, aioresponse
    ):
        aioresponse.get(
            "https://www.amazon.co.jp/s?i=stripbooks&ref=nb_sb_noss&k=url",
            status=200,
            body=str(amazon),
        )
        aioresponse.get(
            "https://m.media-amazon.com/images/I/61Hph+T004L._AC_UY218_.jpg",
            status=429,
            repeat=True,
        )
        res = await shoseki_container.get_image("url", "date")
        assert res == None

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
        manga_updates_title,
        manga_updates_list,
    ):
        aioresponse.get(
            shoseki_container.main_info_parser._MAIN_URL + "暁のARIA",
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

    @mock.patch(
        "src.data_scraping.main_scrapers.shoseki_scraper.ShosekiWeeklyScraper._get_original_title"
    )
    @mock.patch(
        "src.data_scraping.main_scrapers.shoseki_scraper.save_image", return_value=None
    )
    @mock.patch(
        "src.data_scraping.aux_scrapers.manga_updates_scraper.MangaUpdatesParser.fetch"
    )
    async def test_retrieve_data(
        self,
        mock_mangaupdates,
        mock_img,
        mock_title,
        shoseki_container,
        shoseki_weekly_list,
        manga_updates_list,
        manga_updates_title,
    ):
        mock_title.side_effect = ["暁のARIA"] * 30
        mock_mangaupdates.side_effect = [manga_updates_list, manga_updates_title] * 30
        with mock.patch.object(
            ShosekiWeeklyScraper,
            "fetch",
            side_effect=[shoseki_weekly_list] + [bytes("img", "utf-8")] * 30,
        ):
            res = await shoseki_container._retrieve_data("url", "date")
            assert len(res) == 30
            for i, x in enumerate(res, start=1):
                assert x.rating == i
                assert x.name == "Akatsuki no Aria"

    @mock.patch(
        "src.data_scraping.main_scrapers.shoseki_scraper.ShosekiWeeklyScraper._get_original_title"
    )
    @mock.patch(
        "src.data_scraping.main_scrapers.shoseki_scraper.save_image", return_value=None
    )
    @mock.patch(
        "src.data_scraping.aux_scrapers.manga_updates_scraper.MangaUpdatesParser.fetch"
    )
    async def test_get_data(
        self,
        mock_mangaupdates,
        mock_img,
        mock_title,
        shoseki_container,
        shoseki_weekly_list,
        shoseki_list,
        manga_updates_list,
        manga_updates_title,
    ):
        mock_title.side_effect = ["暁のARIA"] * 30
        mock_mangaupdates.side_effect = [manga_updates_list, manga_updates_title] * 30
        with mock.patch.object(
            ShosekiWeeklyScraper,
            "fetch",
            side_effect=[shoseki_list, shoseki_weekly_list]
            + [bytes("img", "utf-8")] * 30,
        ):
            res = await shoseki_container.get_data("2022-10-04")
            assert len(res) == 30
            for i, x in enumerate(res, start=1):
                assert x.rating == i
                assert x.name == "Akatsuki no Aria"
