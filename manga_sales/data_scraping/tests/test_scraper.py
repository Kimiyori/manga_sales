import datetime
import unittest
from unittest.mock import patch

from manga_sales.data_scraping.exceptions import BSError
from .. session_context_manager import Session
from .. web_scraper import OriconScraper
from bs4 import BeautifulSoup
import asyncio


class TestOriconScraper(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.scraper = OriconScraper(Session)

    def test_rating_success(self):
        text = BeautifulSoup("""
                                <div class="inner-label">
						            <p class="num ">1</p>
                                </div>
                            """,
                             'html.parser')
        rating = self.scraper._get_rating(text)
        self.assertEqual(rating, 1)

    def test_rating_fail_not_found(self):
        text = BeautifulSoup("""
                                <div class="inner-label">
                                </div>
                            """,
                             'html.parser')
        rating = self.scraper._get_rating(text)
        self.assertEqual(rating, 0)

    def test_rating_fail_not_decimal(self):
        text = BeautifulSoup("""
                                <div class="inner-label">
                                    <p class="num ">something</p>
                                </div>
                            """,
                             'html.parser')
        rating = self.scraper._get_rating(text)
        self.assertEqual(rating, 0)

    def test_volume_success(self):
        text = BeautifulSoup("""
                        <h2 class="title" itemprop="name">東京卍リベンジャーズ 29</h2>
                            """,
                             'html.parser')
        volume = self.scraper._get_volume(text)
        self.assertEqual(volume, 29)

    def test_volume_fail_not_found(self):
        text = BeautifulSoup("""
                        <h2 itemprop="name">東京卍リベンジャーズ 29</h2>
                            """,
                             'html.parser')
        volume = self.scraper._get_volume(text)
        self.assertEqual(volume, None)

    def test_volume_fail_without_volume_info(self):
        text = BeautifulSoup("""
                        <h2 class="title" itemprop="name">東京卍リベンジャーズ </h2>
                            """,
                             'html.parser')
        volume = self.scraper._get_volume(text)
        self.assertEqual(volume, None)

    def test_release_date_success(self):
        text = BeautifulSoup("""
                            <ul class="list">
								<li>発売日：2022年08月</li>
							</ul>
                            """,
                             'html.parser')
        date = self.scraper._get_release_date(text)
        self.assertEqual(date, datetime.date(2022, 8, 1))

    def test_release_date_fail_not_found(self):
        text = BeautifulSoup("""
                            <ul class="list">
								<li>出版社：講談社</li>
							</ul>
                            """,
                             'html.parser')
        date = self.scraper._get_release_date(text)
        self.assertEqual(date, None)

    def test_release_date_fail_not_match(self):
        text = BeautifulSoup("""
                            <ul class="list">
                                <li>発売日：2022.08</li>
							</ul>
                            """,
                             'html.parser')
        date = self.scraper._get_release_date(text)
        self.assertEqual(date, None)

    def test_sold_success(self):
        text = BeautifulSoup("""
                            <ul class="list">
								<li>推定売上部数：147,741部</li>
							</ul>
                            """,
                             'html.parser')
        date = self.scraper._get_sold_amount(text)
        self.assertEqual(date, 147.741)

    def test_sold_fail_not_found(self):
        text = BeautifulSoup("""
                            <ul class="list">
								<li>推部数：147,741部</li>
							</ul>
                            """,
                             'html.parser')
        date = self.scraper._get_sold_amount(text)
        self.assertEqual(date, 0)

    def test_sold_fail_not_match(self):
        text = BeautifulSoup("""
                            <ul class="list">
								<li>推部数：147741</li>
							</ul>
                            """,
                             'html.parser')
        date = self.scraper._get_sold_amount(text)
        self.assertEqual(date, 0)

    @patch('manga_sales.data_scraping.web_scraper.OriconScraper.fetch')
    async def test_title_success(self, mock):
        text = BeautifulSoup("""
            <h2 class="title" itemprop="name">東京卍リベンジャーズ 29</h2>
                            """,
                             'html.parser')

        mock.side_effect = [BeautifulSoup("""
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
            """, 'html.parser'),
                            BeautifulSoup("""
            <span class="releasestitle tabletitle">Toukyou卍Revengers</span> 
            """, 'html.parser')]

        title, _ = await self.scraper._get_title(text)
        self.assertEqual(title, 'Toukyou卍Revengers')

    async def test_title_fail_not_find_tag(self):
        text = BeautifulSoup("""
            <h2  itemprop="name">東京卍リベンジャーズ 29</h2>
                            """,
                             'html.parser')

        with self.assertRaises(BSError) as error:
            await self.scraper._get_title(text)
            self.assertTrue(
                'Can\'t parse to find title name' in str(error.exception))

    def test_authors_success(self):
        text = BeautifulSoup("""<div class="sCat">
                                    <b>Author(s)</b>
                                </div>
                                <div class="sContent">
                                    <a title="Author Info"><u>WAKUI Ken</u></a>
                                </div>""",
                             'html.parser')
        authors = self.scraper._get_authors(text)
        self.assertEqual(authors, ['WAKUI Ken'])

    def test_authors_fail_not_found(self):
        text = BeautifulSoup("""<div class="sCat">
                                    <b>Not AUthors</b>
                                </div>
                                <div class="sContent">
                                    <a title="Author Info"><u>WAKUI Ken</u></a>
                                </div>""",
                             'html.parser')
        authors = self.scraper._get_authors(text)
        self.assertEqual(authors, [])
    
    def test_publishers_success(self):
        text = BeautifulSoup("""<div class="sCat"><b>Original Publisher</b></div>
                                <div class="sContent"><a  title="Publisher Info"><u>Kodansha</u></a>
</div>""",
                             'html.parser')
        authors = self.scraper._get_publishers(text)
        self.assertEqual(authors, ['Kodansha'])

    def test_publishers_fail_not_found(self):
        text = BeautifulSoup("""<div class="sCat"><b>OPublishsers></div>
                                <div class="sContent"><a title="Publisher Info"><u>Kodansha</u></a>
</div>""",
                             'html.parser')
        authors = self.scraper._get_publishers(text)
        self.assertEqual(authors, [])
