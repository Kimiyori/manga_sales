from dependency_injector import containers, providers
from src.manga_sales.db.data_access_layers.author import AuthorDAO
from src.manga_sales.db.data_access_layers.item import ItemDAO
from src.manga_sales.db.data_access_layers.publisher import PublisherDAO
from src.manga_sales.db.data_access_layers.source import SourceDAO
from src.manga_sales.db.data_access_layers.source_type import SourceTypeDAO
from src.manga_sales.db.data_access_layers.title import TitleDAO
from src.manga_sales.db.data_access_layers.week import WeekDAO
from src.db.session import session as db_session


class DatabaseContainer(containers.DeclarativeContainer):
    """Container for dao layer"""

    wiring_config = containers.WiringConfiguration(
        packages=[
            "src.manga_scrapers.database_handler",
            "src.manga_scrapers.test.test_db_handler",
            "src.manga_scrapers.services.db_service",
            "src.manga_sales.views",
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
