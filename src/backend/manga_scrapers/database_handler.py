# pyright: reportMissingModuleSource=false
from __future__ import annotations
import datetime
from dependency_injector.wiring import Provide, inject, Closing
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine.row import Row

from manga_scrapers.scrapers.rating_scrapers.meta import MainDataAbstractScraper
from manga_scrapers.dataclasses import Content
from manga_scrapers.services.files_service import delete_images

from manga_sales.containers import DatabaseContainer
from manga_sales.db.data_access_layers.author import AuthorDAO
from manga_sales.db.data_access_layers.item import ItemDAO
from manga_sales.db.data_access_layers.publisher import PublisherDAO
from manga_sales.db.data_access_layers.source_type import SourceTypeDAO
from manga_sales.db.data_access_layers.title import TitleDAO
from manga_sales.db.data_access_layers.week import WeekDAO
from manga_sales.db.models import (
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
    Class for handling scraped data and insert it into db
    """

    def __init__(
        self,
        scraper: MainDataAbstractScraper,
    ) -> None:
        self.scraper = scraper

    @staticmethod
    @inject
    async def handle_authors(
        authors: list[str],
        author_session: AuthorDAO = Closing[Provide[DatabaseContainer.authors]],
    ) -> list[Author]:
        """Method fo detecting whether given authors already exist in db or not
            and converting author names to instances of author model

        Args:
            authors (list[str]): list of strings with author names
            author_session (AuthorDAO, optional): Instance of Data object layer for author table.
                Defaults to Closing[Provide[DatabaseContainer.authors]].

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
        name: str, title_session: TitleDAO = Closing[Provide[DatabaseContainer.title]]
    ) -> Title:
        """Method fo detecting whether given title name already exist in db or not
            and converting it to instances of title model

        Args:
            name (str): title name
            title_session (TitleDAO, optional): Instance of Data object layer for title table.
                Defaults to Closing[Provide[DatabaseContainer.title]].

        Returns:
            Title: Instance of title table
        """
        title = await title_session.filter_by_name(name)
        if not title:
            title = Title(name=name)
            title_session.add(title)
        return title

    @staticmethod
    @inject
    async def handle_publishers(
        publishers: list[str],
        publishers_session: PublisherDAO = Closing[
            Provide[DatabaseContainer.publishers]
        ],
    ) -> list[Publisher]:
        """Method fo detecting whether given publishers already exist in db or not
            and converting publisher names to instances of publisher model

        Args:
            publishers (list[str]):list of strings with publishers names
            publishers_session (PublisherDAO, optional): Instance of Data object layer
            for publisher table.Defaults to Closing[ Provide[DatabaseContainer.publishers] ].

        Returns:
            list[Publisher]:  list with Publishers either new or already existing in db
        """
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
            Provide[DatabaseContainer.source_type]
        ],
    ) -> Row | None:
        """Method for getting instance of source_type that used in scraper for connecting week
            that will be created with its source type. If method fail to find given source type
            for given source, then it throws assertion exception.


        Args:
            source_type_session (SourceTypeDAO, optional): Instance of Data object
            layer for source type table.
             Defaults to Closing[ Provide[DatabaseContainer.source_type] ].

        Returns:
            SourceType | None: Instance of source type table
        """
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
        item_session: ItemDAO = Closing[Provide[DatabaseContainer.item]],
    ) -> PreviousRank | None:
        """Method for getting rating place in previous week for given title.

        Args:
            prev_week (Week): Week instance
            current_rank (int): rank that title has in current week
            title (str): name of title
            item_session (ItemDAO, optional): Instance of Data object layer for item table.
             Defaults to Closing[Provide[DatabaseContainer.item]].

        Returns:
            PreviousRank | None: return previous rank enum object.
        """
        prev_rank_item = await item_session.get_previous_rank(
            prev_week, current_rank, title
        )
        return prev_rank_item

    @inject
    async def create_item(
        self,
        content: Content,
        prev_week: Week | None,
        item_session: ItemDAO = Closing[Provide[DatabaseContainer.item]],
    ) -> Item:
        authors = await self.handle_authors(content.authors)
        title = await self.handle_title(content.name)
        publishers = await self.handle_publishers(content.publishers)
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
        item_session.add(item)
        return item

    @staticmethod
    async def get_previous_week(
        week: Week, source_type: SourceType | Row, week_session: WeekDAO
    ) -> Week | None:
        prev_week = await week_session.get_previous_week(week, source_type)
        return prev_week

    @inject
    async def insert_data(
        self,
        date: datetime.date,
        week_session: WeekDAO = Closing[Provide[DatabaseContainer.week]],
        session: AsyncSession = Closing[Provide[DatabaseContainer.session]],  # type: ignore
    ) -> None:
        """Main methof for inserting scraper data in database.

        Args:
            date (datetime.date): date from with need to scrape and get data
            for given site
            week_session (WeekDAO, optional): Instance of Data object layer for week table.
             Defaults to Closing[Provide[DatabaseContainer.week]].

        Raises:
            exc: raises an exception and deletes already saved images (if any)
            if something went wrong during the process of writing
            data to the database or scraping.
        """
        date_str: str = date.strftime("%Y-%m-%d")
        try:
            data = await self.scraper.get_data(date_str)
            if data:
                source_type = await self.get_source_type()
                assert source_type is not None
                week = Week(date=date, source_type_id=source_type.id)
                items = []
                prev_week = await self.get_previous_week(
                    week, source_type, week_session
                )
                for content in data:
                    item = await self.create_item(content, prev_week)
                    items.append(item)
                week.items.extend(items)
                week_session.add(week)
                await session.commit()

        except Exception as exc:
            delete_images(self.scraper.SOURCE, self.scraper.SOURCE_TYPE, date_str)
            raise exc
