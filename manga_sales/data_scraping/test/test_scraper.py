import datetime
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from manga_sales.data_scraping.dataclasses import Content
from manga_sales.data_scraping.exceptions import BSError, NotFound
from manga_sales.data_scraping.session_context_manager import Session
from manga_sales.data_scraping.web_scraper import OriconScraper
from bs4 import BeautifulSoup
from operator import add


class TestOriconScraper(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.scraper = OriconScraper(Session)

    def test_rating_success(self):
        text = BeautifulSoup(
            """
                <div class="inner-label">
                    <p class="num ">1</p>
                </div>
            """,
            "html.parser",
        )
        rating = self.scraper._get_rating(text)
        self.assertEqual(rating, 1)

    def test_rating_fail_not_found(self):
        text = BeautifulSoup(
            """
                                <div class="inner-label">
                                </div>
                            """,
            "html.parser",
        )
        rating = self.scraper._get_rating(text)
        self.assertEqual(rating, 0)

    def test_rating_fail_not_decimal(self):
        text = BeautifulSoup(
            """
                                <div class="inner-label">
                                    <p class="num ">something</p>
                                </div>
                            """,
            "html.parser",
        )
        rating = self.scraper._get_rating(text)
        self.assertEqual(rating, 0)

    def test_volume_success(self):
        text = BeautifulSoup(
            """
                        <h2 class="title" itemprop="name">東京卍リベンジャーズ 29</h2>
                            """,
            "html.parser",
        )
        volume = self.scraper._get_volume(text)
        self.assertEqual(volume, 29)

    def test_volume_fail_not_found(self):
        text = BeautifulSoup(
            """
                        <h2 itemprop="name">東京卍リベンジャーズ 29</h2>
                            """,
            "html.parser",
        )
        volume = self.scraper._get_volume(text)
        self.assertEqual(volume, None)

    def test_volume_fail_without_volume_info(self):
        text = BeautifulSoup(
            """
                        <h2 class="title" itemprop="name">東京卍リベンジャーズ </h2>
                            """,
            "html.parser",
        )
        volume = self.scraper._get_volume(text)
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
        date = self.scraper._get_release_date(text)
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
        date = self.scraper._get_release_date(text)
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
        date = self.scraper._get_release_date(text)
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
        date = self.scraper._get_sold_amount(text)
        self.assertEqual(date, 147.741)

    def test_sold_fail_not_found(self):
        text = BeautifulSoup(
            """
            <ul class="list">
                <li>推部数：147,741部</li>
            </ul>
            """,
            "html.parser",
        )
        date = self.scraper._get_sold_amount(text)
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
        date = self.scraper._get_sold_amount(text)
        self.assertEqual(date, 0)

    @patch("manga_sales.data_scraping.web_scraper.OriconScraper.fetch")
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

        title, _ = await self.scraper._get_title(text)
        self.assertEqual(title, "Toukyou卍Revengers")

    async def test_title_fail_not_find_tag(self):
        text = BeautifulSoup(
            """
            <h2  itemprop="name">東京卍リベンジャーズ 29</h2>
                            """,
            "html.parser",
        )

        with self.assertRaises(BSError) as error:
            await self.scraper._get_title(text)
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
        authors = self.scraper._get_authors(text)
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
        authors = self.scraper._get_authors(text)
        self.assertEqual(authors, [])

    def test_publishers_success(self):
        text = BeautifulSoup(
            """<div class="sCat"><b>Original Publisher</b></div>
                                <div class="sContent"><a  title="Publisher Info"><u>Kodansha</u></a>
</div>""",
            "html.parser",
        )
        authors = self.scraper._get_publishers(text)
        self.assertEqual(authors, ["Kodansha"])

    def test_publishers_fail_not_found(self):
        text = BeautifulSoup(
            """<div class="sCat"><b>OPublishsers></div>
                                <div class="sContent"><a title="Publisher Info"><u>Kodansha</u></a>
</div>""",
            "html.parser",
        )
        authors = self.scraper._get_publishers(text)
        self.assertEqual(authors, [])

    @patch("manga_sales.data_scraping.web_scraper.uuid.uuid4")
    @patch("manga_sales.data_scraping.web_scraper.OriconScraper.fetch")
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
        mock.return_value = "image file"
        mock_uuid.return_value = "uuid_name"
        name, image = await self.scraper._get_image(text)
        self.assertEqual(name, "uuid_name.jpg")
        self.assertEqual(image, "image file")

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

        image = await self.scraper._get_image(text)
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

        image = await self.scraper._get_image(text)
        self.assertEqual(image, None)

    @patch.multiple(
        "manga_sales.data_scraping.web_scraper.OriconScraper",
        _get_rating=MagicMock(side_effect=[1, 2]),
        _get_image=AsyncMock(
            side_effect=[("image name1", "image file1"), ("image name2", "image file2")]
        ),
        _get_title=AsyncMock(return_value=("title", "title_url")),
        _get_authors=MagicMock(return_value=[]),
        _get_publishers=MagicMock(return_value=[]),
        _get_volume=MagicMock(return_value=11),
        _get_release_date=MagicMock(return_value=2022),
        _get_sold_amount=MagicMock(return_value=22),
    )
    @patch("manga_sales.data_scraping.web_scraper.OriconScraper.fetch")
    async def test_retrieve_data_success(self, mock_fetch, **mocks):
        mock_fetch.return_value = BeautifulSoup(
            """
            <section class="box-rank-entry" itemprop="itemListElement" itemscope="" itemtype="http://schema.org/ListItem">
            </section>
            <section class="box-rank-entry" itemprop="itemListElement" itemscope="" itemtype="http://schema.org/ListItem">
            </section>
            """,
            "html.parser",
        )

        await self.scraper.retrieve_data("1")
        result_data = [
            Content(
                name="title",
                volume=11,
                image="image name1",
                imageb="image file1",
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
                imageb="image file2",
                authors=[],
                publisher=[],
                release_date=2022,
                rating=2,
                sold=22,
            ),
        ]
        self.assertEqual(self.scraper.rating_list, result_data)

    @patch("manga_sales.data_scraping.web_scraper.OriconScraper.fetch")
    async def test_retrive_data_fail_no_class(self, mock_fetch):
        mock_fetch.return_value = BeautifulSoup(
            """<section  >
        </section><section>
        </section>""",
            "html.parser",
        )
        with self.assertRaises(BSError) as error:
            await self.scraper.retrieve_data("1")
            self.assertTrue(
                "Fail to find class with titles list" in str(error.exception)
            )

    @patch("manga_sales.data_scraping.web_scraper.OriconScraper.retrieve_data")
    async def test_get_data_success(self, mock):
        data = [
            Content(
                name="title",
                volume=122,
                image="image name1",
                imageb="image file1",
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
                imageb="image file1",
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
                imageb="image file1",
                authors=[],
                publisher=[],
                release_date=2022,
                rating=3,
                sold=45,
            ),
        ]
        mock.side_effect = [self.scraper.rating_list.append(item) for item in data]
        result = await self.scraper.get_data("2022-08-09")
        self.assertEqual(data, result)

    @patch(
        "manga_sales.data_scraping.web_scraper.OriconScraper.fetch",
        side_effect=[NotFound("1"), NotFound("1"), "s"],
    )
    async def test_find_latest_date(self, mock):
        correct_date = add(datetime.date.today(), datetime.timedelta(days=2))
        date = await self.scraper.find_latest_date(add)
        self.assertEqual(date, correct_date)
