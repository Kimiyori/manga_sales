from dependency_injector import containers, providers
from src.data_scraping.main_scrapers.oricon_scraper import OriconWeeklyScraper
from src.data_scraping.main_scrapers.shoseki_scraper import ShosekiWeeklyScraper
from src.data_scraping.services.session_service import session_factory
from src.data_scraping.session_context_manager import Session


class DataScrapingContainer(containers.DeclarativeContainer):
    """Container for scrap dependencies"""

    wiring_config = containers.WiringConfiguration(
        packages=[
            "src.data_scraping.database_saver",
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
