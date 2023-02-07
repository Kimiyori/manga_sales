from __future__ import annotations
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
    Enum,
)
from sqlalchemy.orm import relationship
from db.base import Base

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
    description = Column(String(), nullable=True)
    image = Column(String, nullable=True, unique=True)
    source_type: list[SourceType] = relationship("SourceType", back_populates="source")
    link: list[Link] = relationship("Link", back_populates="source")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(" f"id={self.id}, name={self.name})>"


class Link(Base):
    """Model for storign links"""

    __tablename__ = "link"
    id = Column(Integer, primary_key=True)
    link = Column(String(512), nullable=False)
    source_id = Column(Integer, ForeignKey("source.id", ondelete="CASCADE"))
    source: Source = relationship("Source", back_populates="link")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(" f"id={self.id}, link={self.link})>"


class SourceType(Base):
    """
    Model that contains types of data ( weekly, monthly ) and
    related with :model: Week and :model: Source
    """

    __tablename__ = "source_type"
    id = Column(Integer, primary_key=True)
    type = Column(String(256), nullable=False)
    source_id = Column(Integer, ForeignKey("source.id", ondelete="CASCADE"))
    source: Source = relationship("Source", back_populates="source_type")
    weeks: list[Week] = relationship("Week", back_populates="source_type")
    __table_args__ = (
        UniqueConstraint("type", "source_id", name="_source_sourcetype_const"),
    )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(" f"id={self.id},type={self.type})>"


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


class PreviousRank(enum.Enum):
    """Types for column Previous_rank

    Args:
        UP : new rank higher that previous
        SAME : new rank the same as prevous
        DOWN : new rank lower that preivous
    """

    UP = "UP"
    SAME = "SAME"
    DOWN = "DOWN"


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
