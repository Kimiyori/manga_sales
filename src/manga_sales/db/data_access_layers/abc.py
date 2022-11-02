# pylint:  disable= too-few-public-methods
from abc import ABC
from typing import ClassVar, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession
from src.manga_sales.db.models import TableType

DAOType = TypeVar("DAOType", bound="AbstractDAO")


class AbstractDAO(ABC):
    """Abstract base class for Data Access Layer"""

    model: ClassVar[TableType] = NotImplemented

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def add(self, item):
        self.session.add(item)

    def add_all(self, items):
        self.session.add_all(items)
