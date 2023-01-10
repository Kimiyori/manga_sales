from abc import abstractmethod

from manga_scrapers.scrapers.meta import AbstractBase


class AbstractImageScraper(AbstractBase):
    """Abstract class for parsing images"""

    _MAIN_URL: str

    @abstractmethod
    async def get_image(
        self, search_name: str, filter_name: str, volume: int | None, tries: int = 5
    ) -> bytes:
        """Main method for fetching image

        Args:
            search_name (str): name used for searching needed title
            filter_name (str): name used to filter among the list of titles
            from the list obtained after searching with search_name
            volume (int): volume integer if exist, else None
            tries (int, optional): number allowed attemts to fail parse. Defaults to 5.
            If it fails, then image will be parsed from another sourse

        Returns:
            bytes: image file
        """
