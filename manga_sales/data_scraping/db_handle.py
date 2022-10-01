from __future__ import annotations

from sqlalchemy import exc
import datetime
from manga_sales.data_scraping.dataclasses import Content
from manga_sales.data_scraping.meta import AbstractScraper
from manga_sales.data_scraping.web_scraper import OriconScraper
from manga_sales.models import Author, Item, Publisher, Title, Week
from manga_sales.data_scraping.session_context_manager import Session
from manga_sales.models import Author, Item, Publisher, Title, Week
from operator import add, sub
from pathlib import Path



class DBWriter:
    """
    Class for handling scraped data and write it into db
    """

    def __init__(self,app,scraper):
        self.database_session = app
        self.scraper: AbstractScraper = scraper()
        self.image_path = 'manga_sales/static/images/oricon/'

    async def handle_authors(self, session, authors: list[str]) -> list[Author]:
        existed_authors: list = await Author.filter_by_name(session, authors)
        new_authors = [Author(name=author) for author in authors
                       if author not in (
            author.name for author in existed_authors
        )]
        session.add_all(new_authors)
        existed_authors.extend(new_authors)
        return existed_authors

    async def handle_title(self, session, name) -> Title:
        check_title = await Title.filter_by_name(session, name)
        if not check_title:
            title = Title(name=name)
            session.add(title)
            return title
        else:
            return check_title[0]

    async def handle_publisher(self, session, publishers: list[str]) -> list[Publisher]:
        existed_publishers: list = await Publisher.filter_by_name(session, publishers)
        new_publishers = [Publisher(name=publisher) for publisher in publishers
                          if publisher not in (
            publisher.name for publisher in existed_publishers
        )]
        session.add_all(new_publishers)
        existed_publishers.extend(new_publishers)
        return existed_publishers

    def save_image(self, file: str, name: str, date: str) -> None:
        if file and name:
            p = Path(f'{self.image_path}{date}')
            p.mkdir(exist_ok=True)
            with open(p / f'{name}', 'wb') as f:
                f.write(file)

    async def get_date(self, session,
                       operator: add | sub,
                       date: datetime.date | None = None
                       ) -> datetime.date:
        if not date:
            date = await Week.get_last_date(session) if operator == add else datetime.date.today()
        valid_date = await self.scraper.find_latest_date(date, operator)
        if valid_date:
            check = await Week.get(session, valid_date)
            if check:
                return await self.get_date(session, operator, valid_date)

        return valid_date

    async def write_data(self, operator: add | sub = add) -> None:
        async with self.database_session.get_session() as session:
            date: datetime.date | None = await self.get_date(session, operator)
            while date:
                datestr: str = date.strftime('%Y-%m-%d')
                data: list[Content] = await self.scraper.get_data(datestr)
                week = Week(date=date)
                items = []
                for item in data:
                    print(item)
                    authors = await self.handle_authors(session, item.authors)
                    title = await self.handle_title(session, item.name)
                    publishers = await self.handle_publisher(session, item.publisher)

                    self.save_image(item.imageb, item.image, datestr)
                    item = Item(rating=item.rating, volume=item.volume, image=item.image,
                                release_date=item.release_date, sold=item.sold)
                    item.title = title
                    item.author.extend(authors)
                    item.publisher.extend(publishers)
                    items.append(item)
                    print(item)
                week.items.extend(items)
                session.add(week)
                date: datetime.date | None = await self.get_date(session, operator, date)
                await session.commit()
 
