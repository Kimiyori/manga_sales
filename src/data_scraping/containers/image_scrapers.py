from dependency_injector import containers, providers
from src.data_scraping.image_scrapers.cdjapan import CDJapanImageScraper
from src.data_scraping.services.session_service import session_factory
from src.data_scraping.session_context_manager import Session


class ImageScrapingContainer(containers.DeclarativeContainer):
    """Container for scrap dependencies"""

    wiring_config = containers.WiringConfiguration(
        packages=[
            "src.data_scraping.main_scrapers.oricon_scraper",
            "src.data_scraping.main_scrapers.shoseki_scraper",
            "src.data_scraping.services.db_service",
        ]
    )
    web_session: providers.Resource[Session] = providers.Resource(
        session_factory, Session
    )
    cdjapan_scraper = providers.Factory(
        CDJapanImageScraper,
        session=web_session,
    )
