from dependency_injector import containers, providers
from manga_scrapers.scrapers.rating_scrapers.oricon_scraper import (
    OriconWeeklyScraper,
)
from manga_scrapers.scrapers.rating_scrapers.shoseki_scraper import (
    ShosekiWeeklyScraper,
)
from manga_scrapers.services.session_service import session_factory
from manga_scrapers.client_handler.session_context_manager import Session


class DataScrapingContainer(containers.DeclarativeContainer):
    """Container for scrap dependencies"""

    wiring_config = containers.WiringConfiguration(
        packages=[
            "manga_scrapers.database_handler",
            "manga_scrapers.services.db_service",
            "manga_scrapers.test.test_db_handler",
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
