# pyright: reportMissingModuleSource=false
from __future__ import annotations
import datetime
from typing import Any, Callable
from sqlalchemy import Column, String, Date, SmallInteger, Integer, ForeignKey, Table
from sqlalchemy.future import select
from sqlalchemy import func, cast, TEXT
from sqlalchemy.sql import distinct
from sqlalchemy.orm import relationship
from .db import Base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine.row import Row
from sqlalchemy.dialects.postgresql import aggregate_order_by


class Week(Base):
    __tablename__ = "week"
    id = Column(Integer, primary_key=True)
    date = Column(Date, unique=True, nullable=False)
    items: list[Item] = relationship("Item", back_populates="week")

    @classmethod
    async def get_all(cls, session: AsyncSession) -> list[Row]:
        weeks = await session.execute(select(cls))
        return weeks.all()

    @classmethod
    async def get(cls, session: AsyncSession, date: datetime.date) -> Row | None:
        week = await session.execute(select(cls).where(cls.date == date))
        return week.first()

    @classmethod
    async def get_last_date(cls, session: AsyncSession) -> datetime.date | None:
        results = await session.execute(select(cls).order_by(cls.date.desc()))
        row = results.first()
        date: datetime.date | None = row.date if row else None
        return date

    @classmethod
    async def get_all_groupby(cls, session: AsyncSession) -> list[Week]:
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
        result = [week[0] for week in data.all()]
        return result


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


class Item(Base):
    __tablename__ = "item"
    id = Column(Integer, primary_key=True)
    rating = Column(SmallInteger, nullable=False)
    volume = Column(SmallInteger)
    release_date = Column(Date)
    sold = Column(Integer, nullable=False)
    image = Column(String, nullable=True, unique=True)
    week_id = Column(Integer, ForeignKey("week.id", ondelete="CASCADE"))
    week: list[Week] = relationship("Week", back_populates="items")
    title: list[Title] = relationship("Title", back_populates="items")
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

    @classmethod
    async def get_count(cls, session: AsyncSession) -> Callable[[Any], int] | Any:
        query = select(func.count(cls.id).label("count"))
        result = await session.execute(query)
        row = result.first()
        c = row.count if row else 0
        return c

    @classmethod
    async def get_instance(cls, session: AsyncSession, date_str: str) -> list[Item]:
        try:
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except TypeError as e:
            raise e
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
        items = [item[0] for item in result.all()]
        return items


class Title(Base):
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
        query = select(cls)
        res = await session.execute(query)
        results = [row[0] for row in res]
        return results

    @classmethod
    async def filter_by_name(cls, session: AsyncSession, name: str) -> Title | None:
        maon_query = select(cls).where(cls.name == name)
        item = await session.execute(maon_query)
        row = item.first()
        result: Title | None = row[0] if row else None
        return result


class Author(Base):
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
        query = select(cls)
        results = await session.execute(query)
        return results.all()

    @classmethod
    async def filter_by_name(
        cls, session: AsyncSession, authors: list[str]
    ) -> list[Author] | list[Any]:
        main_query = select(cls).where(cls.name.in_(authors))
        results = await session.execute(main_query)
        list_authors: list[Author | None] = [author[0] for author in results.all()]
        return list_authors


class Publisher(Base):
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
    ) -> list[Publisher] | list[Any]:
        main_query = select(cls).where(cls.name.in_(publishers))
        results = await session.execute(main_query)
        list_publishers: list[Publisher | None] = [
            publisher[0] for publisher in results.all()
        ]
        return list_publishers
