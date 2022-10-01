
from abc import ABCMeta, abstractmethod
from manga_sales.data_scraping.session_context_manager import Session




class AbstractScraper(metaclass=ABCMeta):

    def __init__(self) -> None:

        self.session = Session()
        self.rating_list = []

    @abstractmethod
    def _get_rating(self, item):
        """
        Get rating from given item
        """
        pass

    @abstractmethod
    def _get_volume(self, item):
        """
        Get rating from given item
        """
        pass

    @abstractmethod
    def _get_title(self, item):
        """
        Get title from given item
        """
        pass

    @abstractmethod
    def _get_authors(self, item):
        """
        Get authors from given item
        """
        pass

    @abstractmethod
    def _get_publishers(self, item):
        """
        Get publishers from given item
        """
        pass

    @abstractmethod
    def _get_release_date(self, item):
        """
        Get release date from given item
        """
        pass

    @abstractmethod
    def _get_sold_amount(self, item):
        """
        Get sold from given item
        """
        pass

    @abstractmethod
    def get_data(self, date):
        """
        Main function for get all data
        """
        pass

    @abstractmethod
    def retrieve_data(self, url):
        """
        Get concrete piece of data
        """
        pass
