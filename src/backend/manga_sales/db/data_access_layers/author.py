from __future__ import annotations
from sqlalchemy.future import select
from sqlalchemy.engine.row import Row
from manga_sales.db.data_access_layers.abc import AbstractDAO
from manga_sales.db.models import Author


class AuthorDAO(AbstractDAO):
    """Data Acess Layer for author table"""

    model = Author

    async def get_all(self) -> list[Row]:
        """Get all authors form table

        Args:
            session (AsyncSession): sql session

        Returns:
            list[Row]: list of rows
        """
        query = select(self.model)
        results = await self.session.execute(query)
        return results.all()

    async def filter_by_name(self, authors: list[str]) -> list[Author]:
        """Filter by name author table

        Args:
            session (AsyncSession): sql session
            authors (list[str]): list of authors names

        Returns:
            list[Author] | list[Any]: list of author rows after filtering if they exist
        """
        main_query = select(self.model).where(self.model.name.in_(authors))
        results = await self.session.execute(main_query)
        list_authors: list[Author] = [author[0] for author in results.all()]
        return list_authors
