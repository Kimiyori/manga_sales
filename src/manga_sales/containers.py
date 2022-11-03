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
    source_session = providers.Resource(session, SourceDAO)
    sourcetype_session = providers.Resource(session, SourceTypeDAO)
    author_session = providers.Resource(session, AuthorDAO)
    item_session = providers.Resource(session, ItemDAO)
    publisher_session = providers.Resource(session, PublisherDAO)
    title_session = providers.Resource(session, TitleDAO)
    week_session = providers.Resource(session, WeekDAO)
