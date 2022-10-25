from __future__ import annotations
import datetime
from sqlalchemy import case, distinct, func
from sqlalchemy.future import select
from sqlalchemy.engine.row import Row
from src.manga_sales.db.data_access_layers.abc import AbstractDAO
from src.manga_sales.db.models import Author, Item, PreviousRank, Publisher, Title, Week


class ItemDAO(AbstractDAO):
    model = Item

    async def get(self, **kwargs: str) -> list[Item]:

        query = select(self.model).filter_by(**kwargs)
        result = await self.session.execute(query)
        return [x[0] for x in result.all()]

    async def get_count(self) -> int:
        query = select(func.count(self.model.id).label("count"))
        result = await self.session.execute(query)
        row = result.first()
        count: int = row.count if row else 0  # type: ignore
        return count

    async def get_previous_rank(self, week: Week, rank: int, title: str) -> Row | None:
        query = (
            select(
                case(
                    (self.model.rating > rank, int(PreviousRank.UP)),
                    (self.model.rating == rank, int(PreviousRank.SAME)),
                    (self.model.rating < rank, int(PreviousRank.DOWN)),
                ).label("rank")
            )
            .join(Title)
            .where(self.model.week_id == week.id, Title.name == title)
            .order_by(self.model.rating)
        )
        result = await self.session.execute(query)
        return result.first()

    async def get_instance(self, date_str: str) -> list[Row]:
        """Get item instance

        Args:
            self.session (Asyncself.Session): sql self.session
            date_str (str): string date

        Raises:
            error: raise TypeError if incorrect date type

        Returns:
            list[Row]: list of item rows with all related data
        """
        try:
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except TypeError as error:
            raise error
        query = (
            select(
                self.model.id,
                self.model.rating,
                self.model.volume,
                self.model.release_date,
                self.model.image,
                self.model.sold,
                Week.date.label("week_date"),
                Title.name.label("title"),
                func.array_agg(distinct(Author.name)).label("authors"),
                func.array_agg(distinct(Publisher.name)).label("publishers"),
            )
            .join(Week)
            .join(Title)
            .join(self.model.author)
            .join(self.model.publisher)
            .filter(Week.date == date)
            .group_by(self.model.id, Week.date, Title.name)
            .order_by(self.model.rating)
        )
        result = await self.session.execute(query)
        return result.all()
