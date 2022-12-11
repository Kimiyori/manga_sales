from abc import abstractmethod

from src.data_scraping.meta import AbstractBase
from src.data_scraping.session_context_manager import Session


class AbstractImageScraper(AbstractBase):
    """Abstract class for parsing images"""

    _MAIN_URL: str

    def __init__(
        self, session: Session, search_name: str, filter_name: str, volume: int
    ) -> None:
        self.search_name = search_name
        self.filter_name = filter_name
        self.volume = volume
        super().__init__(session)

    @abstractmethod
    async def get_image(self, tries: int = 5) -> bytes:
        pass
