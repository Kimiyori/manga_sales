

from datetime import datetime
from manga_sales.data_scraping.web_scraper import OriconScraper
from manga_sales.models import Author, Item, Publisher, Title, Week
from manga_sales.data_scraping.session_context_manager import Session
from manga_sales.models import Author, Item, Publisher, Title, Week
from operator import add, sub
from pathlib import Path


class DBWriter:

    def __init__(self, app):
        self.database_session = app
        self.scraper = OriconScraper(Session)
        self.image_path = 'manga_sales/static/images/oricon/'

    async def handle_authors(self, session, authors):
        existed_authors = await Author.filter_by_name(session, authors)
        existed_authors = [author[0] for author in existed_authors]
        new_authors = [Author(name=author) for author in authors
                       if author not in [
            author.name for author in existed_authors
        ]]
        session.add_all(new_authors)
        existed_authors.extend(new_authors)
        return existed_authors

    async def handle_title(self, session, name):
        check_title = await Title.filter_by_name(session, name)

        if not check_title:
            title = Title(name=name)
            session.add(title)
            return title
        else:
            return check_title[0]

    async def handle_publisher(self, session, publishers):
        existed_publishers = await Publisher.filter_by_name(session, publishers)
        existed_publishers = [publisher[0] for publisher in existed_publishers]
        new_publishers = [Publisher(name=publisher) for publisher in publishers
                          if publisher not in [
            publisher.name for publisher in existed_publishers
        ]]
        session.add_all(new_publishers)
        existed_publishers.extend(new_publishers)
        return existed_publishers

    async def get_date(self, session):
        last_row = await Week.get_last_row(session)
        date = await self.scraper.find_latest_date(operator=add if last_row else sub)
        return date

    def handle_image(self, file, name, date):
        p = Path(f'{self.image_path}{date}')
        p.mkdir(exist_ok=True)
        with open(p / f'{name}', 'wb') as f:
            f.write(file)

    async def write_data(self):
        async with self.database_session.get_session as session:
            date = await self.get_date(session)
            datestr = date.strftime('%Y-%m-%d')
            data = await self.scraper.get_data(datestr)
            week = Week(date=date)
            items = []
            for item in data:
                authors = await self.handle_authors(session, item.authors)
                title = await self.handle_title(session, item.name)
                publishers = await self.handle_publisher(session, item.publisher)

                self.handle_image(item.imageb, item.image, datestr)

                item = Item(rating=item.rating, volume=item.volume, image=item.image,
                            release_date=item.release_date, sold=item.sold)

                item.title = title
                item.author.extend(authors)
                item.publisher.extend(publishers)
                items.append(item)
            week.items.extend(items)
            session.add(week)
            await session.commit()
