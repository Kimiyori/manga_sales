from typing import TYPE_CHECKING, TypeAlias
from src.config import get_postgres_uri
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession

if TYPE_CHECKING:
    TSession: TypeAlias = sessionmaker[  # pylint: disable=unsubscriptable-object
        AsyncSession
    ]
else:
    # anything that doesn't raise an exception
    TSession: TypeAlias = AsyncSession


Base = declarative_base()
engine: AsyncEngine = create_async_engine(
    get_postgres_uri(),
    future=True,
    echo=True,
)
Session: TSession = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
