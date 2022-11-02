# pyright: reportMissingModuleSource=false
from __future__ import annotations
from dependency_injector.wiring import Provide, inject, Closing
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from src.data_scraping.containers import DBSessionContainer
from src.data_scraping.meta import ChartItemDataParserAbstract
from src.data_scraping.dataclasses import Content
from src.manga_sales.db.data_access_layers.author import AuthorDAO
from src.manga_sales.db.data_access_layers.item import ItemDAO
from src.manga_sales.db.data_access_layers.publisher import PublisherDAO
from src.manga_sales.db.data_access_layers.source_type import SourceTypeDAO
from src.manga_sales.db.data_access_layers.title import TitleDAO
from src.manga_sales.db.data_access_layers.week import WeekDAO
from src.manga_sales.db.models import (
    Author,
    Item,
    PreviousRank,
    Publisher,
    SourceType,
    Title,
    Week,
)


class DatabaseConnector:
    """
    Class for handling scraped data and write it into db
    """

    @inject
    def __init__(
        self,
        scraper: ChartItemDataParserAbstract,
        session: AsyncSession = Closing[Provide[DBSessionContainer.session]],
    ) -> None:
        self.session = session
        self.scraper = scraper

    @staticmethod
    @inject
    async def handle_authors(
        authors: list[str],
        author_session: AuthorDAO = Closing[Provide[DBSessionContainer.authors]],
    ) -> list[Author]:
        """Function fo detecting whether given authors already exist in db or not
            and converting author names to instances of author model

        Args:
            session (AsyncSession): sql session
            authors (list[str]): list of strings with author names

        Returns:
            list[Author]: list with Authors either new or already existing in db
        """
        existed_authors = await author_session.filter_by_name(authors)
        new_authors = [
            Author(name=author)
            for author in authors
            if author not in [author.name for author in existed_authors]
        ]
        author_session.add_all(new_authors)
        existed_authors.extend(new_authors)
        return existed_authors

    @staticmethod
    @inject
    async def handle_title(
        name: str, title_session: TitleDAO = Closing[Provide[DBSessionContainer.title]]
    ) -> Title:
        title = await title_session.filter_by_name(name)
        if not title:
            title = Title(name=name)
            title_session.add(title)
        return title

    @staticmethod
    @inject
    async def handle_publisher(
        publishers: list[str],
        publishers_session: PublisherDAO = Closing[
            Provide[DBSessionContainer.publishers]
        ],
    ) -> list[Publisher]:
        existed_publishers = await publishers_session.filter_by_name(publishers)
        new_publishers = [
            Publisher(name=publisher)
            for publisher in publishers
            if publisher not in [publisher.name for publisher in existed_publishers]
        ]
        publishers_session.add_all(new_publishers)
        existed_publishers.extend(new_publishers)
        return existed_publishers

    @inject
    async def get_source_type(
        self,
        source_type_session: SourceTypeDAO = Closing[
            Provide[DBSessionContainer.source_type]
        ],
    ) -> SourceType | None:
        source_type = await source_type_session.get_by_source(
            self.scraper.SOURCE, self.scraper.SOURCE_TYPE
        )
        return source_type

    @staticmethod
    @inject
    async def get_previous_place(
        prev_week: Week,
        current_rank: int,
        title: str,
        item_session: ItemDAO = Closing[Provide[DBSessionContainer.item]],
    ) -> PreviousRank | None:
        prev_rank_item = await item_session.get_previous_rank(
            prev_week, current_rank, title
        )
        return prev_rank_item.rank if prev_rank_item else None

    async def create_item(self, content: Content, prev_week: Week | None) -> Item:
        authors = await self.handle_authors(content.authors)
        title = await self.handle_title(content.name) 
        publishers = await self.handle_publisher(content.publishers)
        item = Item(
            rating=content.rating,
            volume=content.volume,
            image=content.image,
            release_date=content.release_date,
            sold=content.sales,
        )
        if prev_week is not None:
            prev_rank = await self.get_previous_place(
                prev_week, content.rating, content.name
            )
            item.previous_rank = prev_rank
        item.title = title
        item.author.extend(authors)
        item.publisher.extend(publishers)
        return item

    @staticmethod
    async def get_previous_week(
        week: Week, source_type: SourceType, week_session : WeekDAO
    ) -> Week | None:
        prev_week = await week_session.get_previous_week(week, source_type)
        return prev_week

    async def write_data(
        self,
        date: datetime.date,
        week_session: WeekDAO = Closing[Provide[DBSessionContainer.week]],
    ) -> None:
        datestr: str = date.strftime("%Y-%m-%d")
        data = await self.scraper.get_data(datestr)
        if data:
            source_type = await self.get_source_type()
            assert source_type is not None
            week = Week(date=date, source_type_id=source_type.id)
            items = []
            prev_week = await self.get_previous_week(week, source_type, week_session)
            for content in data:
                item = await self.create_item(content, prev_week)
                items.append(item)
            week.items.extend(items)
            week_session.add(week)
            await self.session.commit()
