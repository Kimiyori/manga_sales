from types import TracebackType
from abc import abstractmethod
from typing import Any, TypeVar
from bs4 import BeautifulSoup
from src.manga_scrapers.scrapers.meta import AbstractBase

_Self = TypeVar("_Self", bound="AuxDataParserAbstract")


class AuxDataParserAbstract(AbstractBase):
    """Abstract class for parser main data"""

    _MAIN_URL: str

    def __call__(self: _Self, title: str, **kwargs: Any) -> _Self:
        self.title = title
        self.__dict__.update(kwargs)
        return self

    @abstractmethod
    async def __aenter__(self: _Self) -> _Self:
        pass

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: type[BaseException],
        exc_tb: type[TracebackType],
    ) -> None:
        pass

    @classmethod
    def __init_subclass__(cls) -> None:
        """A class method designed to check that all necessary class variables
            are specified in any of its subclasses

        Raises:
            NotImplementedError: raises error of any of required class variables
            is not setted in subclass
        """
        if not cls.__subclasses__():
            required_class_variables = list(cls.__annotations__.keys())
            for var in required_class_variables:
                if not hasattr(cls, var):
                    raise NotImplementedError(
                        f"Class {cls} lacks required `{var}` class attribute"
                    )

    @abstractmethod
    async def get_main_info_page(self) -> BeautifulSoup:
        """Get page from whitch can be collected main info about title
        Args:
            title (str): the name of the title of the page need to get
        Returns:
            BeautifulSoup: bs page
        """

    @abstractmethod
    async def get_image(self) -> bytes | None:
        """Get image file from item and save it

        Args:
            item (BeautifulSoup | str): item from which need to get either
                image or necessary data for it extraction
            date (str): date string

        Returns:
            str | None: name saved image
        """

    @abstractmethod
    def get_authors(self) -> list[str]:
        """Parse page to get list of authors from it

        Args:
            page (BeautifulSoup): bs page

        Returns:
            list[str]: list with strings of authors name
        """

    @abstractmethod
    def get_publishers(self) -> list[str]:
        """Parse page to get list of publishers from it

        Args:
            page (BeautifulSoup): bs page

        Returns:
            list[str]: list with strings of publishers name
        """

    @abstractmethod
    def get_title(self) -> str:
        """Get title from page and get page for main info

        Args:
            page (BeautifulSoup): bs item from which extract title

        Returns:
            tuple[str, BeautifulSoup]: (title name, page with main info)
        """
