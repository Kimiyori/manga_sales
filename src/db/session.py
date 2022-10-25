from typing import AsyncGenerator, Callable
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.base import Session
from src.manga_sales.db.data_access_layers.abc import DAOType


async def session(
    model: Callable[[AsyncSession], DAOType]
) -> AsyncGenerator[DAOType, None]:
    async with Session() as session_obj:
        yield model(session_obj)
