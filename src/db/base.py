from asyncio import current_task
from typing import TYPE_CHECKING, TypeAlias
from src.config import get_postgres_uri
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
)

if TYPE_CHECKING:
    TSession: TypeAlias = async_scoped_session
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
