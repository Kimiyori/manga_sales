from sqlalchemy.engine.row import Row
from sqlalchemy.future import select
from src.manga_sales.db.models import Source
from src.manga_sales.db.data_access_layers.abc import AbstractDAO


class SourceDAO(AbstractDAO):
    """Data Acess Layer for source table"""

    model = Source

    async def get_all(self) -> list[Row]:
        """Gel all sources from table

        Args:
            session (AsyncSession): sql session

        Returns:
            list[Row]: list all week rows
        """
        query = await self.session.execute(select(self.model.name, self.model.image))
        return query.all()
