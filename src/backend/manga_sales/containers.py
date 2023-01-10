from dependency_injector import containers, providers
from manga_sales.db.data_access_layers.author import AuthorDAO
from manga_sales.db.data_access_layers.item import ItemDAO
from manga_sales.db.data_access_layers.publisher import PublisherDAO
from manga_sales.db.data_access_layers.source import SourceDAO
from manga_sales.db.data_access_layers.source_type import SourceTypeDAO
from manga_sales.db.data_access_layers.title import TitleDAO
from manga_sales.db.data_access_layers.week import WeekDAO
from db.session import session as db_session


class DatabaseContainer(containers.DeclarativeContainer):
    """Container for dao layer"""

    wiring_config = containers.WiringConfiguration(
        packages=[
            "manga_scrapers.database_handler",
            "manga_scrapers.test.test_db_handler",
            "manga_scrapers.services.db_service",
            "manga_sales.views",
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
