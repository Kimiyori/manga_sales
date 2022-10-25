from __future__ import annotations
import datetime
import enum
from typing import Type, Union
from sqlalchemy import (
    Column,
    String,
    Date,
    SmallInteger,
    Integer,
    ForeignKey,
    Table,
    UniqueConstraint,
    func,
    cast,
    TEXT,
    case,
    Enum,
)
from sqlalchemy.future import select
from sqlalchemy.sql import distinct
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine.row import Row
from sqlalchemy.dialects.postgresql import aggregate_order_by
from src.db.base import Base

TableType = Union[
    Type["Source"],
    Type["SourceType"],
    Type["Item"],
    Type["Author"],
    Type["Publisher"],
    Type["Week"],
    Type["Title"],
]


class Source(Base):
    """
    Model that contains name and images sources of data like Oricon,Shoseki etc.
    Related to :model: SourceType
    """

    __tablename__ = "source"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False, unique=True)
    image = Column(String, nullable=True, unique=True)
    source_type: list[SourceType] = relationship("SourceType", back_populates="source")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(" f"id={self.id},name={self.name})>"

    @classmethod
    async def get_all(cls, session: AsyncSession) -> list[Row]:
        """Gel all sources from table

        Args:
            session (AsyncSession): sql session

        Returns:
            list[Row]: list all week rows
        """
        query = await session.execute(select(cls.name, cls.image))
        return query.all()


class SourceType(Base):
    """
    Model that contains types of data ( weekly, monthly ) and
    related with :model: Week and :model: Source
    """

    __tablename__ = "source_type"
    id = Column(Integer, primary_key=True)
    type = Column(String(256), nullable=False)
    weeks: list[Week] = relationship("Week", back_populates="source_type")
    source_id = Column(Integer, ForeignKey("source.id", ondelete="CASCADE"))
    source: Source = relationship("Source", back_populates="source_type")
    __table_args__ = (
        UniqueConstraint("type", "source_id", name="_source_sourcetype_const"),
    )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(" f"id={self.id},type={self.type})>"

    @classmethod
    async def get(cls, session: AsyncSession, source: str) -> list[SourceType | None]:
        """Get source type given on source argument

        Args:
            session (AsyncSession): sql session
            source (str): source name that need to extract

        Returns:
            list[Row]: list of sourcetype rows
        """
        query = select(cls).join(Source).where(Source.name == source.capitalize())
        result = await session.execute(query)
        return [x[0] for x in result.all()]

    @classmethod
    async def get_by_source(
        cls, session: AsyncSession, source: str, source_type: str
    ) -> SourceType | None:
        """Get source type given on source argument

        Args:
            session (AsyncSession): sql session
            source (str): source name that need to extract

        Returns:
            list[Row]: list of sourcetype rows
        """
        query = await session.execute(
            select(cls)
            .join(Source)
            .where(
                Source.name == source.capitalize(), cls.type == source_type.capitalize()
            )
        )
        row = query.first()
        result: SourceType | None = row[0] if row else None
        return result


class Week(Base):
    """
    Model that contains weeks and
    related with :model: SourceType and :model: Items
    """

    __tablename__ = "week"
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    source_type_id = Column(Integer, ForeignKey("source_type.id", ondelete="CASCADE"))
    source_type: SourceType = relationship("SourceType", back_populates="weeks")
    items: list[Item] = relationship("Item", back_populates="week")
    __table_args__ = (
        UniqueConstraint("date", "source_type_id", name="_source_week_const"),
    )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(" f"id={self.id},date={self.date})>"

    @classmethod
    async def get_all(cls, session: AsyncSession) -> list[Row]:
        """Gel all weeks from table

        Args:
            session (AsyncSession): sql session

        Returns:
            list[Row]: list of week rows
        """
        weeks = await session.execute(select(cls))
        return weeks.all()

    @classmethod
    async def get(cls, session: AsyncSession, date: datetime.date) -> Row | None:
        """Get week row given on date argument

        Args:
            session (AsyncSession): sql session
            date (datetime.date): _description_

        Returns:
            Row | None: week row if exist else None
        """
        week = await session.execute(select(cls).where(cls.date == date))
        return week.first()

    @classmethod
    async def get_last_date(
        cls, session: AsyncSession, source: str, source_type: str
    ) -> datetime.date | None:
        """Get latest week in table based in desc date filter

        Args:
            session (AsyncSession): sql session

        Returns:
            datetime.date | None: date if table not empty else None
        """
        tpe = await SourceType.get_by_source(session, source, source_type)
        assert tpe is not None
        query = (
            select(cls)
            .where(cls.source_type_id == tpe.id)
            .order_by(cls.date.desc())
            .limit(1)
        )
        results = await session.execute(query)
        row = results.first()
        date: datetime.date | None = row[0].date if row else None
        return date

    @classmethod
    async def get_all_groupby(
        cls, session: AsyncSession, source: str, source_type: str
    ) -> list[Week]:
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
        week_type = await SourceType.get_by_source(session, source, source_type)
        assert week_type is not None
        year = func.extract("year", cls.date).label("year")

        month_str = (
            func.to_char(
                func.to_date(cast(func.extract("month", cls.date), TEXT), "FMMM"),
                "FMMonth",
            )
            .label("month_str")
            .label("month_str")
        )

        aggregate_dates = func.json_agg(
            aggregate_order_by(func.extract("day", cls.date), cls.date)
        ).label("dates")

        inner_maon_query = (
            select(
                year,
                month_str,
                func.extract("month", cls.date).label("month_int"),
                aggregate_dates,
            )
            .where(cls.source_type_id == week_type.id)
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

        data = await session.execute(main_query)
        return data.scalars().all()

    @classmethod
    async def get_previous_week(
        cls, session: AsyncSession, week: Week, source_type: SourceType
    ) -> Week | None:
        """Methof for getting previous week

        Args:
            session (AsyncSession): sql session
            week (Week): Week instance

        Returns:
            Row | None: row with previous week with prev attribute if exist
        """

        main_query = (
            select(cls)
            .where(cls.date < week.date, cls.source_type_id == source_type.id)
            .order_by(cls.date.desc())
            .limit(1)
        )
        query = await session.execute(main_query)
        result = query.first()
        return result[0] if result else None


association_item_author = Table(
    "association_item_author",
    Base.metadata,
    Column("item_id", ForeignKey("item.id")),
    Column("author_id", ForeignKey("author.id")),
)
association_item_publisher = Table(
    "association_item_publisher",
    Base.metadata,
    Column("item_id", ForeignKey("item.id")),
    Column("publisher_id", ForeignKey("publisher.id")),
)


class PreviousRank(enum.IntEnum):
    """Types for column Previous_rank

    Args:
        UP : new rank higher that previous
        SAME : new rank the same as prevous
        DOWN : new rank lower that preivous
    """

    UP = 2
    SAME = 1
    DOWN = 0


class Item(Base):
    """
    Model of main data for title
    """

    __tablename__ = "item"
    id = Column(Integer, primary_key=True)
    rating = Column(SmallInteger, nullable=False)
    volume = Column(SmallInteger)
    release_date = Column(Date)
    previous_rank = Column(Enum(PreviousRank), nullable=True)
    sold = Column(Integer, nullable=True)
    image = Column(String, nullable=True, unique=True)
    week_id = Column(Integer, ForeignKey("week.id", ondelete="CASCADE"))
    week: Week = relationship("Week", back_populates="items")
    title: Title = relationship("Title", back_populates="items")
    title_id = Column(Integer, ForeignKey("title.id", ondelete="CASCADE"))
    author: list[Author] = relationship(
        "Author",
        secondary=association_item_author,
        back_populates="items",
        cascade="all, delete",
    )
    publisher: list[Publisher] = relationship(
        "Publisher",
        secondary=association_item_publisher,
        back_populates="items",
        cascade="all, delete",
    )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(" f"id={self.id})>"

    @classmethod
    async def get(cls, session: AsyncSession, **kwargs: str | Base) -> list[Item]:

        query = select(cls).filter_by(**kwargs)
        result = await session.execute(query)
        return [x[0] for x in result.all()]

    @classmethod
    async def get_count(cls, session: AsyncSession) -> int:
        query = select(func.count(cls.id).label("count"))
        result = await session.execute(query)
        row = result.first()
        count: int = row.count if row else 0  # type: ignore
        return count

    @classmethod
    async def get_previous_rank(
        cls, session: AsyncSession, week: Week, rank: int, title: str
    ) -> Row | None:
        query = (
            select(
                case(
                    (cls.rating > rank, int(PreviousRank.UP)),
                    (cls.rating == rank, int(PreviousRank.SAME)),
                    (cls.rating < rank, int(PreviousRank.DOWN)),
                ).label("rank")
            )
            .join(Title)
            .where(cls.week_id == week.id, Title.name == title)
            .order_by(cls.rating)
        )
        result = await session.execute(query)
        return result.first()

    @classmethod
    async def get_instance(cls, session: AsyncSession, date_str: str) -> list[Row]:
        """Get item instance

        Args:
            session (AsyncSession): sql session
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
                cls.id,
                cls.rating,
                cls.volume,
                cls.release_date,
                cls.image,
                cls.sold,
                Week.date.label("week_date"),
                Title.name.label("title"),
                func.array_agg(distinct(Author.name)).label("authors"),
                func.array_agg(distinct(Publisher.name)).label("publishers"),
            )
            .join(Week)
            .join(Title)
            .join(cls.author)
            .join(cls.publisher)
            .filter(Week.date == date)
            .group_by(cls.id, Week.date, Title.name)
            .order_by(cls.rating)
        )
        result = await session.execute(query)
        return result.all()


class Title(Base):
    """
    Model for titles name
    """

    __tablename__ = "title"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False, unique=True)
    items: list[Item] = relationship("Item", back_populates="title")

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}(" f"id={self.id}, " f"name={self.name}" f")>"
        )

    @classmethod
    async def get_all(cls, session: AsyncSession) -> list[Title]:
        """Returns all names

        Args:
            session (AsyncSession): sql session

        Returns:
            list[Title]: list of titles
        """
        query = select(cls)
        res = await session.execute(query)
        results = [row[0] for row in res]
        return results

    @classmethod
    async def filter_by_name(cls, session: AsyncSession, name: str) -> Title | None:
        """Filtering table by given name

        Args:
            session (AsyncSession): sql session
            name (str): name title

        Returns:
            Title | None: title if exist else None
        """
        maon_query = select(cls).where(cls.name == name)
        item = await session.execute(maon_query)
        row = item.first()
        result: Title | None = row[0] if row else None
        return result


class Author(Base):
    """
    Model for author names
    """

    __tablename__ = "author"
    id: int = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False, unique=True)
    items: list[Item] = relationship(
        "Item", secondary=association_item_author, back_populates="author"
    )

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}(" f"id={self.id}, " f"name={self.name}" f")>"
        )

    @classmethod
    async def get_all(cls, session: AsyncSession) -> list[Row]:
        """Get all authors form table

        Args:
            session (AsyncSession): sql session

        Returns:
            list[Row]: list of rows
        """
        query = select(cls)
        results = await session.execute(query)
        return results.all()

    @classmethod
    async def filter_by_name(
        cls, session: AsyncSession, authors: list[str]
    ) -> list[Author]:
        """Filter by name author table

        Args:
            session (AsyncSession): sql session
            authors (list[str]): list of authors names

        Returns:
            list[Author] | list[Any]: list of author rows after filtering if they exist
        """
        main_query = select(cls).where(cls.name.in_(authors))
        results = await session.execute(main_query)
        list_authors: list[Author] = [author[0] for author in results.all()]
        return list_authors


class Publisher(Base):
    """
    Model for publisher names
    """

    __tablename__ = "publisher"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False, unique=True)
    items: list[Item] = relationship(
        "Item", secondary=association_item_publisher, back_populates="publisher"
    )

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}(" f"id={self.id}, " f"name={self.name}" f")>"
        )

    @classmethod
    async def filter_by_name(
        cls, session: AsyncSession, publishers: list[str]
    ) -> list[Publisher]:
        """Filter by name publisher table

        Args:
            session (AsyncSession): sql session
            authors (list[str]): list of publisher names

        Returns:
            list[Author] | list[Any]: list of publisher rows after filtering if they exist
        """
        main_query = select(cls).where(cls.name.in_(publishers))
        results = await session.execute(main_query)
        list_publishers: list[Publisher] = [publisher[0] for publisher in results.all()]
        return list_publishers
