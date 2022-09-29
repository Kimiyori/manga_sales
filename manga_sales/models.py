
from datetime import datetime

import datetime
from sqlalchemy import Column, DateTime, String, Date, SmallInteger, Integer, ForeignKey, Table,DECIMAL
from sqlalchemy import delete as sqlalchemy_delete
from sqlalchemy import update as sqlalchemy_update
from sqlalchemy.future import select
from sqlalchemy import func, cast, TEXT, delete
from sqlalchemy.sql import text, distinct
from sqlalchemy.orm import relationship, aliased
from .db import Base


class Week(Base):
    __tablename__ = "week"
    id = Column(Integer, primary_key=True)
    date = Column(Date, unique=True, nullable=False)
    items = relationship('Item', back_populates='week')


    @classmethod
    async def get_all(cls, session):
        weeks = await session.execute(select(cls))
        return weeks.all()

    @classmethod
    async def get(cls, session, date):
        week = await session.execute(select(cls).where(cls.date==date))
        return week.fetchone()


    @classmethod
    async def get_last_row(cls, session):
        row = await session.execute(select(cls).order_by(cls.id.desc()))
        row = row.first()
        return row

    @classmethod
    async def get_all_groupby(cls, session):
        year = func.extract('year', cls.date).label('year')

        month = func.to_char(
            func.to_date(
                cast(
                    func.extract(
                        'month', cls.date), TEXT),
                'FMMM'),
            'FMMonth'
        ).label('month')

        aggregate_dates = func.json_agg(cls.date).label('dates')

        inner_maon_query = select(
            year,
            month,
            aggregate_dates,
        ).group_by('year', 'month'
                   ).order_by(
            'year', 'month').subquery()

        aggregate_month = select(
            inner_maon_query.c.year,
            func.json_object_agg(
                inner_maon_query.c.month,
                inner_maon_query.c.dates
            ).label('dates2')
        ).group_by(inner_maon_query.c.year).subquery()

        main_query = select(
            func.json_object_agg(
                aggregate_month.c.year,
                aggregate_month.c.dates2
            )
        ).group_by(aggregate_month.c.year)

        data = await session.execute(main_query)
        data = data.all()
        result = [item[0] for item in data]
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
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    rating = Column(SmallInteger, nullable=False)
    volume = Column(SmallInteger)
    release_date = Column(Date)
    sold = Column(Integer, nullable=False)
    image = Column(String, nullable=True, unique=True)
    week_id = Column(Integer, ForeignKey('week.id', ondelete="CASCADE"))
    week = relationship('Week', back_populates='items')
    title = relationship('Title', back_populates='items')
    title_id = Column(Integer, ForeignKey('title.id', ondelete="CASCADE"))
    author = relationship(
        'Author', secondary=association_item_author, back_populates='items', cascade="all, delete",)
    publisher = relationship(
        'Publisher', secondary=association_item_publisher, back_populates='items', cascade="all, delete",)

    @classmethod
    async def get_count(cls,session):
        query= select(func.count(cls.id).label('count'))
        result=await session.execute(query)
        return result.first().count


    @classmethod
    async def get_instance(cls, session, date):
        try:
            date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        except TypeError as e:
            raise e
        query = select(
            cls.id, cls.rating, cls.volume,
            cls.release_date, cls.image, cls.sold,
            Week.date.label('week_date'), Title.name.label('title'),
            func.array_agg(
                distinct(Author.name)
            ).label('authors'),
            func.array_agg(
                distinct(Publisher.name)
            ).label('publishers')
        ).join(
            Week
        ).join(
            Title
        ).join(cls.author
               ).join(cls.publisher
                      ).filter(Week.date == date
                               ).group_by(
            cls.id, Week.date, Title.name
        ).order_by(cls.rating)
        result = await session.execute(query)
        return result.all()


class Title(Base):
    __tablename__ = 'title'
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False, unique=True)
    items = relationship('Item', back_populates='title')

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"name={self.name}"
            f")>"
        )

    @classmethod
    async def get_all(cls,session):
        query=select(cls)
        results=await session.execute(query)
        return results.all()
    @classmethod
    async def filter_by_name(cls, session, name):
        maon_query = select(cls).where(cls.name == name)
        item = await session.execute(maon_query)
        return item.first()


class Author(Base):
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False, unique=True)
    items = relationship(
        'Item', secondary=association_item_author, back_populates='author')

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"name={self.name}"
            f")>"
        )

    @classmethod
    async def get_all(cls,session):
        query=select(cls)
        results=await session.execute(query)
        return results.all()

    @classmethod
    async def filter_by_name(cls, session, authors):
        main_query = select(cls).where(cls.name.in_(authors))
        results = await session.execute(main_query)
        list_authors=[author[0] for author in results.all()]
        return list_authors

class Publisher(Base):
    __tablename__ = 'publisher'
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False, unique=True)
    items = relationship(
        'Item', secondary=association_item_publisher, back_populates='publisher')

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"name={self.name}"
            f")>"
        )

    @classmethod
    async def filter_by_name(cls, session, publishers):
        main_query = select(cls).where(cls.name.in_(publishers))
        results = await session.execute(main_query)
        list_publishers=[publisher[0] for publisher in results.all()]
        return list_publishers
