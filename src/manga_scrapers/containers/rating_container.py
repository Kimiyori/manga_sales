from dependency_injector import containers, providers
from src.manga_scrapers.scrapers.rating_scrapers.oricon_scraper import (
    OriconWeeklyScraper,
)
from src.manga_scrapers.scrapers.rating_scrapers.shoseki_scraper import (
    ShosekiWeeklyScraper,
)
from src.manga_scrapers.services.session_service import session_factory
from src.manga_scrapers.client_handler.session_context_manager import Session


class DataScrapingContainer(containers.DeclarativeContainer):
    """Container for scrap dependencies"""

    wiring_config = containers.WiringConfiguration(
        packages=[
            "src.data_scraping.database_handler",
            "src.data_scraping.services.db_service",
            "src.data_scraping.test.test_db_handler",
        ]
    )
    web_session: providers.Resource[Session] = providers.Resource(
        session_factory, Session
    )
    oricon_scraper = providers.Factory(
        OriconWeeklyScraper,
        session=web_session,
    )
    shoseki_scraper = providers.Factory(ShosekiWeeklyScraper, session=web_session)
