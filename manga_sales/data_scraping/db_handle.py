# pyright: reportMissingModuleSource=false
from __future__ import annotations
from typing import Callable
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from manga_sales.data_scraping.meta import ChartItemDataParserAbstract
from manga_sales.db import AsyncDatabaseSession
from manga_sales.models import (
    Author,
    Item,
    PreviousRank,
    Publisher,
    SourceType,
    Title,
    Week,
)


class DBWriter:
    """
    Class for handling scraped data and write it into db
    """

    def __init__(
        self,
        app: AsyncDatabaseSession,
        scraper: Callable[[], ChartItemDataParserAbstract],
    ) -> None:
        self.database_session = app
        self.scraper = scraper()
        self.image_path: str = "manga_sales/static/images/oricon/"

    @staticmethod
    async def handle_authors(session: AsyncSession, authors: list[str]) -> list[Author]:
        """Function fo detecting whether given authors already exist in db or not
            and converting author names to instances of author model

        Args:
            session (AsyncSession): sql session
            authors (list[str]): list of strings with author names

        Returns:
            list[Author]: list with Authors either new or already existing in db
        """
        existed_authors = await Author.filter_by_name(session, authors)
        new_authors = [
            Author(name=author)
            for author in authors
            if author not in [author.name for author in existed_authors]
        ]
        session.add_all(new_authors)
        existed_authors.extend(new_authors)
        return existed_authors

    @staticmethod
    async def handle_title(session: AsyncSession, name: str) -> Title:
        check_title = await Title.filter_by_name(session, name)
        if not check_title:
            title = Title(name=name)
            session.add(title)
            return title
        return check_title

    @staticmethod
    async def handle_publisher(
        session: AsyncSession, publishers: list[str]
    ) -> list[Publisher]:
        existed_publishers = await Publisher.filter_by_name(session, publishers)
        new_publishers = [
            Publisher(name=publisher)
            for publisher in publishers
            if publisher not in [publisher.name for publisher in existed_publishers]
        ]
        session.add_all(new_publishers)
        existed_publishers.extend(new_publishers)
        return existed_publishers

    async def get_source_type(self, session: AsyncSession) -> SourceType | None:
        source_type = await SourceType.get_by_source(
            session, self.scraper.SOURCE, self.scraper.SOURCE_TYPE
        )
        return source_type

    @staticmethod
    async def get_previous_week(
        session: AsyncSession, week: Week, source_type: SourceType
    ) -> Week | None:
        prev_week = await Week.get_previous_week(session, week, source_type)
        return prev_week

    @staticmethod
    async def get_previous_place(
        session: AsyncSession, prev_week: Week, current_rank: int, title: str
    ) -> PreviousRank | None:
        prev_rank_item = await Item.get_previous_rank(
            session, prev_week, current_rank, title
        )
        return prev_rank_item.rank if prev_rank_item else None

    async def get_date(
        self,
        session: AsyncSession,
        date: datetime.date | None = None,
    ) -> datetime.date | None:
        if not date:
            check_date = await Week.get_last_date(
                session, self.scraper.SOURCE, self.scraper.SOURCE_TYPE
            )
            date = check_date if check_date else datetime.date.today()
        valid_date: datetime.date | None = await self.scraper.find_latest_date(date)
        if valid_date:
            check = await Week.get(session, valid_date)
            if check:
                return await self.get_date(session, valid_date)
        return valid_date

    async def write_data(self) -> None:
        async with self.database_session.get_session() as session:
            date: datetime.date | None = await self.get_date(session)
            while date:
                datestr: str = date.strftime("%Y-%m-%d")
                data = await self.scraper.get_data(datestr)
                if not data:
                    break
                source_type = await self.get_source_type(session)
                assert source_type is not None
                week = Week(date=date, source_type_id=source_type.id)
                items = []
                prev_week = await self.get_previous_week(session, week, source_type)
                for content in data:
                    authors = await self.handle_authors(session, content.authors)
                    title = await self.handle_title(session, content.name)
                    publishers = await self.handle_publisher(session, content.publisher)
                    item = Item(
                        rating=content.rating,
                        volume=content.volume,
                        image=content.image,
                        release_date=content.release_date,
                        sold=content.sold,
                    )
                    if prev_week is not None:
                        prev_rank = await self.get_previous_place(
                            session, prev_week, content.rating, content.name
                        )
                        item.previous_rank = prev_rank
                    item.title = title
                    item.author.extend(authors)
                    item.publisher.extend(publishers)
                    items.append(item)
                week.items.extend(items)
                session.add(week)
                await session.commit()
                date: datetime.date | None = await self.get_date(session, date)  # type: ignore
