from sqlalchemy.future import select
from manga_sales.db.models import Title
from manga_sales.db.data_access_layers.abc import AbstractDAO


class TitleDAO(AbstractDAO):
    """Data Acess Layer for title table"""

    model = Title

    async def get_all(self) -> list[Title]:
        """Returns all names

        Args:
            session (AsyncSession): sql session

        Returns:
            list[Title]: list of titles
        """
        query = select(self.model)
        res = await self.session.execute(query)
        results = [row[0] for row in res]
        return results

    async def filter_by_name(self, name: str) -> Title | None:
        """Filtering table by given name

        Args:
            session (AsyncSession): sql session
            name (str): name title

        Returns:
            Title | None: title if exist else None
        """
        maon_query = select(self.model).where(self.model.name == name)
        item = await self.session.execute(maon_query)
        row = item.first()
        result: Title | None = row[0] if row else None
        return result
