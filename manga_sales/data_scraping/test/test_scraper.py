import datetime
import shutil
import unicodedata
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from manga_sales.data_scraping.dataclasses import Content
from manga_sales.data_scraping.exceptions import BSError, NotFound
from manga_sales.data_scraping.web_scraper import (
    OriconWeeklyScraper,
    ShosekiWeeklyScraper,
)
from bs4 import BeautifulSoup
from operator import add


class TestOriconWeeklyScraper(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.scraper = OriconWeeklyScraper()
        self.date = "2022-02-12"

    def tearDown(self):
        try:
            shutil.rmtree(f"manga_sales/static/images/oricon/weekly/{self.date}")
        except OSError:
            pass

    def test_rating_success(self):
        text = BeautifulSoup(
            """
                <div class="inner-label">
                    <p class="num ">1</p>
                </div>
            """,
            "html.parser",
        )
        rating = self.scraper.get_rating(text)
        self.assertEqual(rating, 1)

    def test_rating_fail_not_found(self):
        text = BeautifulSoup(
            """
            <div class="inner-label"></div>
            """,
            "html.parser",
        )
        with self.assertRaises(AttributeError):
            self.scraper.get_rating(text)

    def test_rating_fail_not_decimal(self):
        text = BeautifulSoup(
            """
            <div class="inner-label">
                <p class="num ">something</p>
            </div>
            """,
            "html.parser",
        )
        with self.assertRaises(ValueError):
            self.scraper.get_rating(text)

    def test_volume_success(self):
        text = BeautifulSoup(
            """
            <h2 class="title" itemprop="name">東京卍リベンジャーズ 29</h2>
            """,
            "html.parser",
        )
        volume = self.scraper.get_volume(text)
        self.assertEqual(volume, 29)

    def test_volume_fail_not_found(self):
        text = BeautifulSoup(
            """
            <h2 itemprop="name">東京卍リベンジャーズ 29</h2>
            """,
            "html.parser",
        )
        volume = self.scraper.get_volume(text)
        self.assertEqual(volume, None)

    def test_volume_fail_without_volume_info(self):
        text = BeautifulSoup(
            """
            <h2 class="title" itemprop="name">東京卍リベンジャーズ </h2>
            """,
            "html.parser",
        )
        volume = self.scraper.get_volume(text)
        self.assertEqual(volume, None)

    def test_release_date_success(self):
        text = BeautifulSoup(
            """
            <ul class="list">
                <li>発売日：2022年08月</li>
            </ul>
            """,
            "html.parser",
        )
        date = self.scraper.get_release_date(text)
        self.assertEqual(date, datetime.date(2022, 8, 1))

    def test_release_date_fail_not_found(self):
        text = BeautifulSoup(
            """
            <ul class="list">
                <li>出版社：講談社</li>
            </ul>
            """,
            "html.parser",
        )
        date = self.scraper.get_release_date(text)
        self.assertEqual(date, None)

    def test_release_date_fail_not_match(self):
        text = BeautifulSoup(
            """
            <ul class="list">
                <li>発売日：2022.08</li>
            </ul>
            """,
            "html.parser",
        )
        date = self.scraper.get_release_date(text)
        self.assertEqual(date, None)

    def test_sold_success(self):
        text = BeautifulSoup(
            """
            <ul class="list">
                <li>推定売上部数：147,741部</li>
            </ul>
            """,
            "html.parser",
        )
        date = self.scraper.get_sale(text)
        self.assertEqual(date, 147741)

    def test_sold_fail_not_found(self):
        text = BeautifulSoup(
            """
            <ul class="list">
                <li>推部数：147,741部</li>
            </ul>
            """,
            "html.parser",
        )
        date = self.scraper.get_sale(text)
        self.assertEqual(date, 0)

    def test_sold_fail_not_match(self):
        text = BeautifulSoup(
            """
            <ul class="list">
                <li>推部数：147741</li>
            </ul>
            """,
            "html.parser",
        )
        date = self.scraper.get_sale(text)
        self.assertEqual(date, 0)

    @patch("manga_sales.data_scraping.web_scraper.OriconWeeklyScraper.fetch")
    async def test_title_success(self, mock):
        text = BeautifulSoup(
            """
            <h2 class="title" itemprop="name">東京卍リベンジャーズ 29</h2>
            """,
            "html.parser",
        )

        mock.side_effect = [
            BeautifulSoup(
                """
            <div class="col-12 col-lg-6 p-3 text">
                <div class="text">
                    <a href="https://www.mangaupdates.com/series/aev98v4/toukyou-wanrevengers" alt="Series Info"><u><b><i>東京卍リベンジャーズ</i></b></u></a>
                </div>
            </div>
            <div class="col-12 col-lg-6 p-3 text">
                <div class="text">
                    <a href="https://www.mangaupdates.com/series/8hvp1dh/tokyo-revengers-dj-yomosugara" alt="Series Info"><u><b><i>東京卍リベンジャーズ dj - よもすがら</i></b></u></a>
                </div>
            </div>
            <div class="col-12 col-lg-6 p-3 text">
                <div class="text">
                    <a href="https://www.mangaupdates.com/series/p5qneev/tokyo-revengers-dj-kiken-na-tora-no-shitsukekata" alt="Series Info"><u><b><i>東京卍リベンジャーズ dj - キケンな虎のしつけかた</i></b></u></a>
                </div>
            </div>
            </div>
            """,
                "html.parser",
            ),
            BeautifulSoup(
                """
            <span class="releasestitle tabletitle">Toukyou卍Revengers</span>
            """,
                "html.parser",
            ),
        ]

        title, _ = await self.scraper.get_title(text)
        self.assertEqual(title, "Toukyou卍Revengers")

    async def test_title_fail_not_find_tag(self):
        text = BeautifulSoup(
            """
            <h2  itemprop="name">東京卍リベンジャーズ 29</h2>
                            """,
            "html.parser",
        )

        with self.assertRaises(BSError) as error:
            await self.scraper.get_title(text)
            self.assertTrue("Can't parse to find title name" in str(error.exception))

    def test_authors_success(self):
        text = BeautifulSoup(
            """<div class="sCat">
                                    <b>Author(s)</b>
                                </div>
                                <div class="sContent">
                                    <a title="Author Info"><u>WAKUI Ken</u></a>
                                </div>""",
            "html.parser",
        )
        authors = self.scraper.get_authors(text)
        self.assertEqual(authors, ["WAKUI Ken"])

    def test_authors_fail_not_found(self):
        text = BeautifulSoup(
            """<div class="sCat">
                                    <b>Not AUthors</b>
                                </div>
                                <div class="sContent">
                                    <a title="Author Info"><u>WAKUI Ken</u></a>
                                </div>""",
            "html.parser",
        )
        authors = self.scraper.get_authors(text)
        self.assertEqual(authors, [])

    def test_publishers_success(self):
        text = BeautifulSoup(
            """<div class="sCat"><b>Original Publisher</b></div>
                                <div class="sContent"><a  title="Publisher Info"><u>Kodansha</u></a>
</div>""",
            "html.parser",
        )
        authors = self.scraper.get_publishers(text)
        self.assertEqual(authors, ["Kodansha"])

    def test_publishers_fail_not_found(self):
        text = BeautifulSoup(
            """<div class="sCat"><b>OPublishsers></div>
                                <div class="sContent"><a title="Publisher Info"><u>Kodansha</u></a>
</div>""",
            "html.parser",
        )
        authors = self.scraper.get_publishers(text)
        self.assertEqual(authors, [])

    @patch("manga_sales.data_scraping.web_scraper.uuid.uuid4")
    @patch("manga_sales.data_scraping.web_scraper.OriconWeeklyScraper.fetch")
    async def test_image_success(self, mock, mock_uuid):
        text = BeautifulSoup(
            """
            <p class="image">
                <span>
                <a href="https://www.oricon.co.jp/book/406528657/" itemprop="url">
                <img src="https://m.media-amazon.com/images/I/51x+1xrAGiL._SL160_.jpg" alt="東京卍リベンジャーズ 29" itemprop="image">
                </a>
                </span>
            </p>
            """,
            "html.parser",
        )
        mock.return_value = b"image file"
        mock_uuid.return_value = "uuid_name"
        name = await self.scraper.get_image(text, self.date)
        self.assertEqual(name, "uuid_name.jpg")

    async def test_image_fail_not_find_class(self):
        text = BeautifulSoup(
            """
            <p >
                <span>
                <a href="https://www.oricon.co.jp/book/406528657/" itemprop="url">
                <img src="https://m.media-amazon.com/images/I/51x+1xrAGiL._SL160_.jpg" alt="東京卍リベンジャーズ 29" itemprop="image">
                </a>
                </span>
            </p>
            """,
            "html.parser",
        )

        image = await self.scraper.get_image(text, self.date)
        self.assertEqual(image, None)

    async def test_image_fail_not_find_src(self):
        text = BeautifulSoup(
            """
            <p  class="image" >
                <span>
                <a href="https://www.oricon.co.jp/book/406528657/" itemprop="url">
                <img alt="東京卍リベンジャーズ 29" itemprop="image">
                </a>
                </span>
            </p>
            """,
            "html.parser",
        )

        image = await self.scraper.get_image(text, self.date)
        self.assertEqual(image, None)

    @patch.multiple(
        "manga_sales.data_scraping.web_scraper.OriconWeeklyScraper",
        get_rating=MagicMock(side_effect=[1, 2]),
        get_image=AsyncMock(side_effect=["image name1", "image name2"]),
        get_title=AsyncMock(return_value=("title", "title_url")),
        get_authors=MagicMock(return_value=[]),
        get_publishers=MagicMock(return_value=[]),
        get_volume=MagicMock(return_value=11),
        get_release_date=MagicMock(return_value=2022),
        get_sale=MagicMock(return_value=22),
    )
    @patch("manga_sales.data_scraping.web_scraper.OriconWeeklyScraper.fetch")
    async def test_retrieve_data_success(self, mock_fetch):
        mock_fetch.return_value = BeautifulSoup(
            """
            <section class="box-rank-entry" itemprop="itemListElement" itemscope="" itemtype="http://schema.org/ListItem">
            </section>
            <section class="box-rank-entry" itemprop="itemListElement" itemscope="" itemtype="http://schema.org/ListItem">
            </section>
            """,
            "html.parser",
        )

        res = await self.scraper._retrieve_data("1", self.date)
        result_data = [
            Content(
                name="title",
                volume=11,
                image="image name1",
                authors=[],
                publisher=[],
                release_date=2022,
                rating=1,
                sold=22,
            ),
            Content(
                name="title",
                volume=11,
                image="image name2",
                authors=[],
                publisher=[],
                release_date=2022,
                rating=2,
                sold=22,
            ),
        ]
        self.assertCountEqual(res, result_data)

    @patch("manga_sales.data_scraping.web_scraper.OriconWeeklyScraper.fetch")
    async def test_retrive_data_fail_no_class(self, mock_fetch):
        mock_fetch.return_value = BeautifulSoup(
            """<section  >
        </section><section>
        </section>""",
            "html.parser",
        )
        with self.assertRaises(BSError) as error:
            await self.scraper._retrieve_data("1", "2022-10-04")
            self.assertTrue(
                "Fail to find class with titles list" in str(error.exception)
            )

    @patch("manga_sales.data_scraping.web_scraper.OriconWeeklyScraper._retrieve_data")
    async def test_get_data_success(self, mock):
        data = [
            Content(
                name="title",
                volume=122,
                image="image name1",
                authors=[],
                publisher=[],
                release_date=2022,
                rating=1,
                sold=13,
            ),
            Content(
                name="title",
                volume=111,
                image="image name1",
                authors=[],
                publisher=[],
                release_date=2022,
                rating=2,
                sold=22,
            ),
            Content(
                name="title",
                volume=113,
                image="image name1",
                authors=[],
                publisher=[],
                release_date=2022,
                rating=3,
                sold=45,
            ),
        ]
        mock.side_effect = [item for item in data]
        result = await self.scraper.get_data("2022-08-09")
        self.assertEqual(data, result)

    @patch(
        "manga_sales.data_scraping.web_scraper.OriconWeeklyScraper.fetch",
        side_effect=[NotFound("1"), NotFound("1"), "s"],
    )
    async def test_find_latest_date(self, mock):
        correct_date = add(datetime.date.today(), datetime.timedelta(days=3))
        date = await self.scraper.find_latest_date(datetime.date.today())
        self.assertEqual(date, correct_date)


class TestShosekiScraper(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.scraper = ShosekiWeeklyScraper()
        self.date = "2022-10-04"

    def tearDown(self):
        try:
            shutil.rmtree(f"manga_sales/static/images/shoseki/weekly/{self.date}")
        except OSError:
            pass

    @patch(
        "manga_sales.data_scraping.web_scraper.ShosekiWeeklyScraper.get_image",
        side_effect=[None, None, None],
    )
    @patch(
        "manga_sales.data_scraping.web_scraper.ShosekiWeeklyScraper._get_list_raw_data",
        return_value=[
            ["1", "9784757581012", "その着せ替え人形は恋をする 10 スクウェア 福田晋一 2022.9.24"],
            ["2", "9784088924250", "キングダム 66 集英社 原泰久 2022.9.16"],
            ["3", "9784867204153", "終末のワルキューレ 16 コアミック アジチカ 2022.9.20"],
        ],
    )
    @patch(
        "manga_sales.data_scraping.web_scraper.ShosekiWeeklyScraper._get_data_url",
        return_value="http://shosekiranking.blog.fc2.com/blog-entry-4115.html",
    )
    async def test_get_data_success(self, mock_url, mock_raw_data, mock_img):
        result = await self.scraper.get_data(self.date)
        guessed_result = [
            Content(
                name="Sono Bisque Doll wa Koi wo suru",
                volume=10,
                image=None,
                authors=["FUKUDA Shinichi"],
                publisher=["Square Enix"],
                release_date=datetime.date(2022, 9, 24),
                rating=1,
                sold=None,
            ),
            Content(
                name="Kingdom",
                volume=66,
                image=None,
                authors=["HARA Yasuhisa"],
                publisher=["Shueisha"],
                release_date=datetime.date(2022, 9, 16),
                rating=2,
                sold=None,
            ),
            Content(
                name="Record of Ragnarok",
                volume=16,
                image=None,
                authors=["FUKUI Takumi", "UMEMURA Shinya"],
                publisher=["Tokuma Shoten"],
                release_date=datetime.date(2022, 9, 20),
                rating=3,
                sold=None,
            ),
        ]
        self.assertEqual(result, guessed_result)

    @patch(
        "manga_sales.data_scraping.web_scraper.ShosekiWeeklyScraper._get_data_url",
        return_value=None,
    )
    async def test_get_data_none(self, mock_url):
        result = await self.scraper.get_data(self.date)
        self.assertEqual(result, None)

    @patch(
        "manga_sales.data_scraping.web_scraper.ShosekiWeeklyScraper.fetch",
        return_value=BeautifulSoup(
            """
            <div class="content">
            <div class="entry_body">1 <a target="_blank"
            href="">
            9784757581012 </a><img src="//ir-jp.amazon-adsystem.com/e/ir?t=shosekicomic-22&amp;l=ur2&amp;o=9" width="1"
            height="1" border="0" alt=""
            style="border: none !important; margin: 0px !important; display: none !important;">  その着せ替え人形は恋をする　１０ スクウェア 福田晋一 2022.9.24<br>2 <a target="_blank"
            href="">
            9784088924250 </a><img src="//ir-jp.amazon-adsystem.com/e/ir?t=shosekicomic-22&amp;l=ur2&amp;o=9" width="1"
            height="1" border="0" alt=""
            style="border: none !important; margin: 0px !important; display: none !important;">  キングダム　６６ 集英社 原泰久 2022.9.16<br>3 <a target="_blank"
            href="">
            9784867204153 </a><img src="//ir-jp.amazon-adsystem.com/e/ir?t=shosekicomic-22&amp;l=ur2&amp;o=9" width="1"
            height="1" border="0" alt=""
            style="border: none !important; margin: 0px !important; display: none !important;">  終末のワルキューレ　１６ コアミック アジチカ 2022.9.20<br>
        """,
            "html.parser",
        ),
    )
    async def test_get_list_raw_data_success(self, mock_fetch):
        raw_expect = [
            ["1", "9784757581012", "その着せ替え人形は恋をする １０ スクウェア 福田晋一 2022.9.24"],
            ["2", "9784088924250", "キングダム ６６ 集英社 原泰久 2022.9.16"],
            ["3", "9784867204153", "終末のワルキューレ １６ コアミック アジチカ 2022.9.20"],
        ]
        expect = [[unicodedata.normalize("NFKC", x) for x in i] for i in raw_expect]
        result = await self.scraper._get_list_raw_data("dummy_url")
        self.assertCountEqual(result, expect)

    @patch(
        "manga_sales.data_scraping.web_scraper.ShosekiWeeklyScraper.fetch",
        return_value=BeautifulSoup(
            """
            <div class="entry_body">1 <a target="_blank"
            href="">
            9784757581012 </a><img src="//ir-jp.amazon-adsystem.com/e/ir?t=shosekicomic-22&amp;l=ur2&amp;o=9" width="1"
            height="1" border="0" alt=""
            style="border: none !important; margin: 0px !important; display: none !important;">  その着せ替え人形は恋をする　１０ スクウェア 福田晋一 2022.9.24<br>
        """,
            "html.parser",
        ),
    )
    async def test_get_list_raw_data_fail_parse(self, mock_fetch):
        with self.assertRaises(AttributeError) as error:
            await self.scraper._get_list_raw_data("dummy_url")
            self.assertTrue(
                "'NoneType' object has no attribute 'find'" in str(error.exception)
            )

    @patch(
        "manga_sales.data_scraping.web_scraper.ShosekiWeeklyScraper.fetch",
        return_value=BeautifulSoup(
            """
        <ul class="list_body">
<li>2022/10/04 : <a href="http://shosekiranking.blog.fc2.com/blog-entry-4115.html" title="2022年9/26-10/2 漫画ランキング コミック売上BEST500【その着せ替え人形は恋をする10】">2022年9/26-10/2 漫画ランキング コミック売上BEST500【その着せ替え人形は恋をする10】</a></li>
<li>2022/09/27 : <a href="http://shosekiranking.blog.fc2.com/blog-entry-4107.html" title="2022年9/19-9/25 漫画ランキング コミック売上BEST500【キングダム66】">2022年9/19-9/25 漫画ランキング コミック売上BEST500【キングダム66】</a></li>
    """,
            "html.parser",
        ),
    )
    async def test_get_data_url_success(self, mock_fetch):
        result = await self.scraper._get_data_url(self.date)
        self.assertEqual(
            result, "http://shosekiranking.blog.fc2.com/blog-entry-4115.html"
        )

        result_none = await self.scraper._get_data_url("2022-10-05")
        self.assertEqual(result_none, None)

    @patch(
        "manga_sales.data_scraping.web_scraper.ShosekiWeeklyScraper.fetch",
        return_value=BeautifulSoup(
            """
<li>2022/10/04 : <a href="http://shosekiranking.blog.fc2.com/blog-entry-4115.html" title="2022年9/26-10/2 漫画ランキング コミック売上BEST500【その着せ替え人形は恋をする10】">2022年9/26-10/2 漫画ランキング コミック売上BEST500【その着せ替え人形は恋をする10】</a></li>
    """,
            "html.parser",
        ),
    )
    async def test_get_data_url_fail_parse(self, mock_fetch):
        with self.assertRaises(AttributeError) as error:
            await self.scraper._get_data_url(self.date)
            self.assertTrue(
                "'NoneType' object has no attribute 'find_all'" in str(error.exception)
            )

    def test_convert_str_to_date_success(self):
        date = self.scraper.convert_str_to_date(self.date)
        self.assertEqual(date, datetime.date(2022, 10, 4))

        date_without_day = self.scraper.convert_str_to_date("2022-10")
        self.assertEqual(date_without_day, datetime.date(2022, 10, 1))

    def test_convert_str_to_date_fail(self):
        with self.assertRaises(AssertionError) as error:
            self.scraper.convert_str_to_date("2022")
            self.assertTrue("Fail match date" in str(error.exception))

    @patch(
        "manga_sales.data_scraping.web_scraper.ShosekiWeeklyScraper.fetch",
        return_value=BeautifulSoup(
            """
        <ul class="list_body">
<li>2022/10/04 : <a href="http://shosekiranking.blog.fc2.com/blog-entry-4115.html" title="2022年9/26-10/2 漫画ランキング コミック売上BEST500【その着せ替え人形は恋をする10】">2022年9/26-10/2 漫画ランキング コミック売上BEST500【その着せ替え人形は恋をする10】</a></li>
<li>2022/09/27 : <a href="http://shosekiranking.blog.fc2.com/blog-entry-4107.html" title="2022年9/19-9/25 漫画ランキング コミック売上BEST500【キングダム66】">2022年9/19-9/25 漫画ランキング コミック売上BEST500【キングダム66】</a></li>
    """,
            "html.parser",
        ),
    )
    async def test_find_latest_date_success(self, mock_fetch):
        result = await self.scraper.find_latest_date(datetime.date(2022, 9, 27))
        self.assertEqual(result, datetime.date(2022, 10, 4))
        result_without_convert = await self.scraper.find_latest_date(
            datetime.date(2022, 9, 27), date_convert=False
        )
        self.assertEqual(
            result_without_convert,
            "2022/10/04 : 2022年9/26-10/2 漫画ランキング コミック売上BEST500【その着せ替え人形は恋をする10】",
        )

        result_none = await self.scraper.find_latest_date(datetime.date(2022, 10, 4))
        self.assertEqual(result_none, None)
        result_none2 = await self.scraper.find_latest_date(datetime.date(2022, 9, 4))
        self.assertEqual(result_none2, None)

    @patch(
        "manga_sales.data_scraping.web_scraper.ShosekiWeeklyScraper.fetch",
        return_value=BeautifulSoup(
            """

<li>2022/10/04 : <a href="http://shosekiranking.blog.fc2.com/blog-entry-4115.html" title="2022年9/26-10/2 漫画ランキング コミック売上BEST500【その着せ替え人形は恋をする10】">2022年9/26-10/2 漫画ランキング コミック売上BEST500【その着せ替え人形は恋をする10】</a></li>
<li>2022/09/27 : <a href="http://shosekiranking.blog.fc2.com/blog-entry-4107.html" title="2022年9/19-9/25 漫画ランキング コミック売上BEST500【キングダム66】">2022年9/19-9/25 漫画ランキング コミック売上BEST500【キングダム66】</a></li>
    """,
            "html.parser",
        ),
    )
    async def test_find_latest_date_file_fail(self, mock_fetch):
        with self.assertRaises(AttributeError):
            await self.scraper.find_latest_date(datetime.datetime(2022, 9, 27))

    async def test_get_rating_success(self):
        res = self.scraper.get_rating("4")
        self.assertEqual(res, 4)

    async def test_get_rating_fail(self):
        with self.assertRaises(ValueError):
            self.scraper.get_rating("a")

    async def test_get_volume_success(self):
        res = self.scraper.get_volume("その着せ替え人形は恋をする 10 スクウェア 福田晋一 2022.9.24")
        self.assertEqual(res, 10)

    async def test_get_volume_fail(self):
        with self.assertRaises(AssertionError):
            self.scraper.get_volume("その着せ替え人形は恋をする スクウェア 福田晋一 2022.9.24")

    def test_get_release_success(self):
        res = self.scraper.get_release_date("その着せ替え人形は恋をする 10 スクウェア 福田晋一 2022.9.24")
        self.assertEqual(res, datetime.date(2022, 9, 24))

    def test_get_release_fail(self):
        res = self.scraper.get_release_date("その着せ替え人形は恋をする スクウェア 福田晋一")
        self.assertEqual(res, None)

    def test_get_original_title_success(self):
        res = self.scraper._get_original_title("その着せ替え人形は恋をする 10 スクウェア 福田晋一 2022.9.24")
        self.assertEqual(res, "その着せ替え人形は恋をする ")
