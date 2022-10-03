
from abc import ABCMeta, abstractmethod
import datetime
from typing import Callable

from bs4 import BeautifulSoup
from manga_sales.data_scraping.dataclasses import Content
from manga_sales.data_scraping.session_context_manager import Session




class AbstractScraper(metaclass=ABCMeta):

    def __init__(self) -> None:

        self.session = Session()
        self.rating_list:list[Content] = []

    @abstractmethod
    def _get_rating(self, item:BeautifulSoup)-> int:
        """
        Get rating from given item
        """
        pass

    @abstractmethod
    def _get_volume(self, item: BeautifulSoup)-> int | None:
        """
        Get rating from given item
        """
        pass

    @abstractmethod
    def _get_title(self,item : BeautifulSoup) ->tuple[str, BeautifulSoup]:
        """
        Get title from given item
        """
        pass

    @abstractmethod
    def _get_authors(self, item: BeautifulSoup)-> list[str]:
        """
        Get authors from given item
        """
        pass

    @abstractmethod
    def _get_publishers(self, item: BeautifulSoup)-> list[str]:
        """
        Get publishers from given item
        """
        pass

    @abstractmethod
    def _get_release_date(self, item: BeautifulSoup)-> datetime.date | None:
        """
        Get release date from given item
        """
        pass

    @abstractmethod
    def _get_sold_amount(self, item: BeautifulSoup)-> int:
        """
        Get sold from given item
        """
        pass

    @abstractmethod
    def get_data(self, date:str)-> list[Content]:
        """
        Main function for get all data
        """
        pass

    @abstractmethod
    def retrieve_data(self, url:str)->None:
        """
        Get concrete piece of data
        """
        pass

    @abstractmethod
    async def find_latest_date(self, date:datetime.date,operator:Callable[[
                                   datetime.date, datetime.timedelta], datetime.datetime])-> datetime.date | None:
        """
        Get concrete piece of data
        """
        pass