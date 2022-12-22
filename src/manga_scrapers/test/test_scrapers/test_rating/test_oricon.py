import datetime
from unittest import mock
import pytest
from src.manga_scrapers.exceptions import BSError, NotFound
from src.manga_scrapers.scrapers.rating_scrapers.oricon_scraper import (
    OriconWeeklyScraper,
)
from src.manga_scrapers.scrapers.rating_scrapers.shoseki_scraper import (
    ShosekiWeeklyScraper,
)
from src.manga_scrapers.utils.url_handler import build_url, update_url
from src.manga_scrapers.test.conftest import (
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
    async def test_get_list_raw_data_success(
        self, aioresponse, oricon_container, oricon_list
    ):
        aioresponse.get(
            "2022-11-11",
            body=str(oricon_list),
        )
        lst = await oricon_container._get_list_raw_data("2022-11-11")
        assert len(lst) == 10

    @pytest.mark.asyncio
    async def test_get_list_raw_data_error(
        self, aioresponse, oricon_container, oricon_list
    ):
        lst = oricon_list.find_all("section", {"class": "box-rank-entry"})
        for x in lst:
            x["class"] = "something"
        aioresponse.get(
            "2022-11-11",
            body=str(oricon_list),
        )
        with pytest.raises(BSError):
            await oricon_container._get_list_raw_data("2022-11-11")

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
    async def test_get_image(self, aioresponse, oricon_container, oricon_item):
        aioresponse.get(
            "https://m.media-amazon.com/images/I/41DRrJAiurL._SL160_.jpg",
            body=bytes("img", "utf-8"),
        )
        img = await oricon_container._get_image(oricon_item)
        assert isinstance(img, bytes)

    @pytest.mark.asyncio
    async def test_find_latest_date(self, aioresponse, oricon_container):
        date = [
            datetime.date(2022, 10, 11) + datetime.timedelta(days=x)
            for x in range(1, 4)
        ]
        for x in date[:-1]:
            aioresponse.get(
                update_url(
                    oricon_container.MAIN_URL,
                    path=[x.strftime("%Y-%m-%d")],
                    trailing_slash=True,
                ),
                status=404,
            )
        aioresponse.get(
            update_url(
                oricon_container.MAIN_URL,
                path=[date[-1].strftime("%Y-%m-%d")],
                trailing_slash=True,
            ),
            body="bingo",
        )
        date = await oricon_container.find_latest_date(
            datetime.date(2022, 10, 11), "forward"
        )
        assert date == datetime.date(2022, 10, 14)

    @pytest.mark.asyncio
    async def test_find_latest_date_none(self, aioresponse, oricon_container):
        date = [
            datetime.date(2022, 10, 11) + datetime.timedelta(days=x)
            for x in range(1, 11)
        ]
        for x in date:
            aioresponse.get(
                update_url(
                    oricon_container.MAIN_URL,
                    path=[x.strftime("%Y-%m-%d")],
                    trailing_slash=True,
                ),
                status=404,
            )
        date = await oricon_container.find_latest_date(
            datetime.date(2022, 10, 11), "forward"
        )
        assert date == None

    @mock.patch("src.manga_scrapers.scrapers.meta.AbstractBase.fetch")
    async def test_get_aux_data(
        self,
        mock,
        oricon_container,
        manga_updates_container,
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

    @mock.patch("src.manga_scrapers.scrapers.meta.AbstractBase.fetch")
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
