import unittest
from .. web_scraper import OriconScraper


class TestOriconScraper(unittest.TestCase):

    def setUp(self) -> None:
        self.scraper = OriconScraper()
