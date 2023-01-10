from typing import AsyncGenerator, Callable
from sqlalchemy.ext.asyncio import AsyncSession
from db.base import Session
from manga_sales.db.data_access_layers.abc import DAOType


async def session(
    model: Callable[[AsyncSession], DAOType] | None = None
) -> AsyncGenerator[DAOType, None] | AsyncSession:
    async with Session() as session_obj:
        yield model(session_obj) if model else session_obj
