from typing import TYPE_CHECKING, TypeAlias
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
)

from config.config import get_postgres_uri

if TYPE_CHECKING:
    TSession: TypeAlias = sessionmaker[  # pylint: disable = unsubscriptable-object
        AsyncSession
    ]
else:
    # anything that doesn't raise an exception
    TSession: TypeAlias = AsyncSession


Base = declarative_base()
async_engine: AsyncEngine = create_async_engine(
    get_postgres_uri(),
    future=True,
    echo=True,
)
# async_session_factory = sessionmaker(async_engine, class_=AsyncSession)
Session: TSession = sessionmaker(async_engine, class_=AsyncSession)
