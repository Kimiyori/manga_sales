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
<<<<<<< HEAD:src/manga_scrapers/containers/image_container.py
            "src.manga_scrapers.services.db_service",
=======
            "src.data_scraping.services.db_service",
>>>>>>> 9fc37800311af0d2921a0e9862583c1c0c093483:src/data_scraping/containers/image_scrapers.py
        ]
    )
    web_session: providers.Resource[Session] = providers.Resource(
        session_factory, Session
    )
    cdjapan_scraper = providers.Factory(
        CDJapanImageScraper,
        session=web_session,
    )
