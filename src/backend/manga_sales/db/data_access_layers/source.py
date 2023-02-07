from sqlalchemy.engine.row import Row
from sqlalchemy.future import select
from sqlalchemy import func
from manga_sales.db.models import Source, Link, SourceType
from manga_sales.db.data_access_layers.abc import AbstractDAO


class SourceDAO(AbstractDAO):
    """Data Access Layer for source table"""

    model = Source

    async def get_all(self) -> list[Row]:
        """Gel all sources from table

        Args:
            session (AsyncSession): sql session

        Returns:
            list[Row]: list all week rows
        """
        query = await self.session.execute(
            select(
                self.model.id,
                self.model.name,
                self.model.image,
                self.model.description,
                Link.link.label("link"),
                func.array_agg(SourceType.type).label("types"),
            )
            .join(Link, isouter=True)
            .join(SourceType)
            .group_by(self.model.id, Link.link)
        )
        return query.all()
