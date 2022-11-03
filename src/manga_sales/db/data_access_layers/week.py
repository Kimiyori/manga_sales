import datetime
from sqlalchemy import TEXT, cast, func
from sqlalchemy.future import select
from sqlalchemy.engine.row import Row
from sqlalchemy.dialects.postgresql import aggregate_order_by
from src.manga_sales.db.data_access_layers.abc import AbstractDAO
from src.manga_sales.db.data_access_layers.source_type import SourceTypeDAO
from src.manga_sales.db.models import SourceType, Week


class WeekDAO(AbstractDAO):
    """Data Acess Layer for week table"""

    model = Week

    async def get_all(self) -> list[Row]:
        """Gel all weeks from table

        Args:
            session (AsyncSession): sql session

        Returns:
            list[Row]: list of week rows
        """
        weeks = await self.session.execute(select(self.model))
        return weeks.all()

    async def get(self, date: datetime.date) -> Row | None:
        """Get week row given on date argument

        Args:
            session (AsyncSession): sql session
            date (datetime.date): _description_

        Returns:
            Row | None: week row if exist else None
        """
        week = await self.session.execute(
            select(self.model).where(self.model.date == date)
        )
        return week.first()

    async def get_last_date(self, source: str, source_type: str) -> Row | None:
        """Get latest week in table based in desc date filter

        Args:
            session (AsyncSession): sql session

        Returns:
            datetime.date | None: date if table not empty else None
        """
        tpe = await SourceTypeDAO(self.session).get_by_source(source, source_type)
        assert tpe is not None
        query = (
            select(self.model)
            .where(self.model.source_type_id == tpe.id)
            .order_by(self.model.date.desc())
            .limit(1)
        )
        results = await self.session.execute(query)
        return results.first()

    async def get_all_groupby(self, source: str, source_type: str) -> list[Week]:
        """
        Get week date with group by by year and month if the following format:

        Example: [
                {
                    '2021':
                    {'September': [05], 'October': [7]},
                    '2022':
                    {'August': [22, 29], 'September': [5, 12, 19, 26], 'October': [3]}
                }
            ]

        Args:
            session (AsyncSession): sql session

        Returns:
            list[Week]: list of weeks with json groupby
        """
        week_type = await SourceTypeDAO(self.session).get_by_source(source, source_type)
        assert week_type is not None
        year = func.extract("year", self.model.date).label("year")

        month_str = (
            func.to_char(
                func.to_date(
                    cast(func.extract("month", self.model.date), TEXT), "FMMM"
                ),
                "FMMonth",
            )
            .label("month_str")
            .label("month_str")
        )

        aggregate_dates = func.json_agg(
            aggregate_order_by(func.extract("day", self.model.date), self.model.date)
        ).label("dates")

        inner_maon_query = (
            select(
                year,
                month_str,
                func.extract("month", self.model.date).label("month_int"),
                aggregate_dates,
            )
            .where(self.model.source_type_id == week_type.id)
            .group_by("year", "month_str", "month_int")
            .order_by("year", "month_int")
            .subquery()
        )

        aggregate_month = (
            select(
                inner_maon_query.c.year,
                func.json_object_agg(
                    inner_maon_query.c.month_str,
                    inner_maon_query.c.dates,
                ).label("dates2"),
            )
            .group_by(inner_maon_query.c.year)
            .subquery()
        )

        main_query = select(
            func.json_object_agg(aggregate_month.c.year, aggregate_month.c.dates2)
        ).group_by(aggregate_month.c.year)

        data = await self.session.execute(main_query)
        return data.scalars().all()

    async def get_previous_week(
        self, week: Week, source_type: SourceType
    ) -> Week | None:
        """Methof for getting previous week

        Args:
            session (AsyncSession): sql session
            week (Week): Week instance

        Returns:
            Row | None: row with previous week with prev attribute if exist
        """

        main_query = (
            select(self.model)
            .where(
                self.model.date < week.date, self.model.source_type_id == source_type.id
            )
            .order_by(self.model.date.desc())
            .limit(1)
        )
        query = await self.session.execute(main_query)
        result = query.first()
        return result[0] if result else None
