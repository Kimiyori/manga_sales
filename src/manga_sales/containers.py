from dependency_injector import containers, providers
from src.manga_sales.db.data_access_layers.author import AuthorDAO
from src.manga_sales.db.data_access_layers.item import ItemDAO
from src.manga_sales.db.data_access_layers.publisher import PublisherDAO
from src.manga_sales.db.data_access_layers.source import SourceDAO
from src.manga_sales.db.data_access_layers.source_type import SourceTypeDAO
from src.manga_sales.db.data_access_layers.title import TitleDAO
from src.manga_sales.db.data_access_layers.week import WeekDAO
from src.db.session import session


class DatabaseContainer(containers.DeclarativeContainer):
    """Container for dao layer"""

    wiring_config = containers.WiringConfiguration(packages=["src.manga_sales.views"])
    session_db = providers.Resource(session)
    source_session = providers.Factory(SourceDAO, session_db)
    sourcetype_session = providers.Factory(SourceTypeDAO, session_db)
    author_session = providers.Factory(AuthorDAO, session_db)
    item_session = providers.Factory(ItemDAO, session_db)
    publisher_session = providers.Factory(PublisherDAO, session_db)
    title_session = providers.Factory(TitleDAO, session_db)
    week_session = providers.Factory(WeekDAO, session_db)
