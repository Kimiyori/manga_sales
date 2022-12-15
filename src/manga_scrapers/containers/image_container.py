from dependency_injector import containers, providers
from src.manga_scrapers.scrapers.image_scrapers.cdjapan import CDJapanImageScraper
from src.manga_scrapers.services.session_service import session_factory
from src.manga_scrapers.client_handler.session_context_manager import Session


class ImageScrapingContainer(containers.DeclarativeContainer):
    """Container for scrap dependencies"""

    wiring_config = containers.WiringConfiguration(
        packages=[
            "src.manga_scrapers.scrapers.rating_scrapers.oricon_scraper",
            "src.manga_scrapers.scrapers.rating_scrapers.shoseki_scraper",
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
