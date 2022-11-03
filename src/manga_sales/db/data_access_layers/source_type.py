from sqlalchemy.future import select
from src.manga_sales.db.data_access_layers.abc import AbstractDAO
from src.manga_sales.db.models import Source, SourceType


class SourceTypeDAO(AbstractDAO):
    """Data Acess Layer for source type table"""

    model = SourceType

    async def get(self, source: str) -> list[SourceType | None]:
        """Get source type given on source argument

        Args:
            session (AsyncSession): sql session
            source (str): source name that need to extract

        Returns:
            list[Row]: list of sourcetype rows
        """
        query = (
            select(self.model).join(Source).where(Source.name == source.capitalize())
        )
        result = await self.session.execute(query)
        return [x[0] for x in result.all()]

    async def get_by_source(self, source: str, source_type: str) -> SourceType | None:
        """Get source type given on source argument

        Args:
            session (AsyncSession): sql session
            source (str): source name that need to extract

        Returns:
            list[Row]: list of sourcetype rows
        """
        query = await self.session.execute(
            select(self.model)
            .join(Source)
            .where(
                Source.name == source.capitalize(),
                self.model.type == source_type.capitalize(),
            )
        )
        row = query.first()
        result: SourceType | None = row[0] if row else None
        return result
