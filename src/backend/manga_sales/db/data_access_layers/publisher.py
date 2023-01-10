from sqlalchemy.future import select
from manga_sales.db.data_access_layers.abc import AbstractDAO
from manga_sales.db.models import Publisher


class PublisherDAO(AbstractDAO):
    """Data Acess Layer for publisher table"""

    model = Publisher

    async def filter_by_name(self, publishers: list[str]) -> list[Publisher]:
        """Filter by name publisher table

        Args:
            session (AsyncSession): sql session
            authors (list[str]): list of publisher names

        Returns:
            list[Author] | list[Any]: list of publisher rows after filtering if they exist
        """
        main_query = select(self.model).where(self.model.name.in_(publishers))
        results = await self.session.execute(main_query)
        list_publishers: list[Publisher] = [publisher[0] for publisher in results.all()]
        return list_publishers
