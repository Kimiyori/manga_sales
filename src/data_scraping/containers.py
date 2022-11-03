from dependency_injector import containers, providers
from src.data_scraping.aux_scrapers.manga_updates_scraper import MangaUpdatesParser
from src.data_scraping.main_scrapers.oricon_scraper import OriconWeeklyScraper
from src.data_scraping.main_scrapers.shoseki_scraper import ShosekiWeeklyScraper
from src.data_scraping.services import session_factory
from src.data_scraping.session_context_manager import Session
from src.manga_sales.db.data_access_layers.author import AuthorDAO
from src.manga_sales.db.data_access_layers.item import ItemDAO
from src.manga_sales.db.data_access_layers.publisher import PublisherDAO
from src.manga_sales.db.data_access_layers.source import SourceDAO
from src.manga_sales.db.data_access_layers.source_type import SourceTypeDAO
from src.manga_sales.db.data_access_layers.title import TitleDAO
from src.manga_sales.db.data_access_layers.week import WeekDAO
from src.db.session import session as db_session


class DataScrapingContainer(containers.DeclarativeContainer):
    """Container for scrap dependencies"""

    web_session = providers.Resource(session_factory, Session)
    manga_updates = providers.Factory(MangaUpdatesParser, web_session)
    oricon_scraper = providers.Factory(
        OriconWeeklyScraper, session=web_session, main_info_parser=manga_updates
    )
    shoseki_scraper = providers.Factory(
        ShosekiWeeklyScraper, session=web_session, main_info_parser=manga_updates
    )


class DBSessionContainer(containers.DeclarativeContainer):
    """Container for database dependensies with common session
            for all table layers

    _
    """

    wiring_config = containers.WiringConfiguration(
        packages=[
            "src.data_scraping.database_saver",
            "src.data_scraping.test.test_db_handler",
        ]
    )
    session = providers.Resource(db_session)
    source = providers.Factory(SourceDAO, session)
    source_type = providers.Factory(SourceTypeDAO, session)
    authors = providers.Factory(AuthorDAO, session)
    item = providers.Factory(ItemDAO, session)
    publishers = providers.Factory(PublisherDAO, session)
    title = providers.Factory(TitleDAO, session)
    week = providers.Factory(WeekDAO, session)
