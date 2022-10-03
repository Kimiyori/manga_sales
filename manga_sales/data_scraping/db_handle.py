# pyright: reportMissingModuleSource=false
from __future__ import annotations
from typing import Callable
import datetime
from typing_extensions import reveal_type
from manga_sales.data_scraping.dataclasses import Content
from manga_sales.data_scraping.meta import AbstractScraper
from manga_sales.db import AsyncDatabaseSession
from manga_sales.models import Author, Item, Publisher, Title, Week
from manga_sales.models import Author, Item, Publisher, Title, Week
from operator import add
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from aiohttp.web import Response

class DBWriter:
    """
    Class for handling scraped data and write it into db
    """

    def __init__(self, app: AsyncDatabaseSession,
                 scraper: Callable[[], AbstractScraper]) -> None:
        self.database_session = app
        self.scraper = scraper()
        self.image_path: str = 'manga_sales/static/images/oricon/'

    async def handle_authors(self, session: AsyncSession,
                             authors: list[str]) -> list[Author]:
        existed_authors = await Author.filter_by_name(session, authors)
        new_authors = [Author(name=author) for author in authors
                       if author not in [
            author.name for author in existed_authors
        ]]
        session.add_all(new_authors)
        existed_authors.extend(new_authors)
        return existed_authors

    async def handle_title(self, session: AsyncSession, name: str) -> Title:
        check_title = await Title.filter_by_name(session, name)
        if not check_title:
            title = Title(name=name)
            session.add(title)
            return title
        else:
            return check_title

    async def handle_publisher(self, session: AsyncSession,
                               publishers: list[str]) -> list[Publisher]:
        existed_publishers = await Publisher.filter_by_name(session, publishers)
        new_publishers = [Publisher(name=publisher) for publisher in publishers
                          if publisher not in [
            publisher.name for publisher in existed_publishers
        ]]
        session.add_all(new_publishers)
        existed_publishers.extend(new_publishers)
        return existed_publishers

    def save_image(self, file: bytes | None, name: str, date: str) -> None:
        if file and name:
            p = Path(f'{self.image_path}{date}')
            p.mkdir(exist_ok=True)
            with open(p / f'{name}', 'wb') as f:
                f.write(file)

    async def get_date(self, session: AsyncSession,
                       operator: Callable[[datetime.datetime, datetime.datetime], datetime.datetime],
                       date: datetime.date | None = None
                       ) -> datetime.date | None:
        if not date:
            date = await Week.get_last_date(session) if operator == add else datetime.date.today()
        valid_date:datetime.date|None = await self.scraper.find_latest_date(date, operator)
        if valid_date:
            check = await Week.get(session, valid_date)
            if check:
                return await self.get_date(session, operator, valid_date)
        return valid_date 

    async def write_data(self, operator: Callable[[datetime.datetime, datetime.datetime], datetime.datetime] = add) -> None:
        async with self.database_session.get_session() as session:
            date: datetime.date | None = await self.get_date(session, operator)
            while date:
                datestr: str = date.strftime('%Y-%m-%d')
                data: list[Content] = await self.scraper.get_data(datestr)
                week = Week(date=date)
                items = []
                for content in data:
                    authors = await self.handle_authors(session, content.authors)
                    title = await self.handle_title(session, content.name)
                    publishers = await self.handle_publisher(session, content.publisher)

                    self.save_image(content.imageb, content.image, datestr)
                    item = Item(rating=content.rating, volume=content.volume, image=content.image,
                                release_date=content.release_date, sold=content.sold)
                    item.title = title
                    item.author.extend(authors)
                    item.publisher.extend(publishers)
                    items.append(item)
                week.items.extend(items)
                session.add(week)
                date: datetime.date | None = await self.get_date(session, operator, date)
                await session.commit()
