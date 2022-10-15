import unittest
from unittest.mock import patch
from manga_sales.data_scraping.dataclasses import Content
from manga_sales.data_scraping.db_handle import DBWriter
from manga_sales.data_scraping.web_scraper import (
    OriconWeeklyScraper,
    ShosekiWeeklyScraper,
)
from manga_sales.db import AsyncDatabaseSession
from manga_sales.test.test_db import AbstractTestDatabase
from manga_sales.models import Author, Item, Publisher, Title, Week
import datetime

AbstractTestDBHandler=1

class TestAuthors(AbstractTestDatabase,unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.authors = [Author(name="test_author"), Author(name="test_author2")]
        async with self.session.get_session() as session:
            session.add_all(self.authors)
            await session.commit()
        self.handler = [
            DBWriter(self.session, OriconWeeklyScraper),
            DBWriter(self.session, ShosekiWeeklyScraper),
        ]

    async def test_handle_authors_single_new(self):
        new_author = ["new_author"]
        async with self.session.get_session() as session:
            for handler in self.handler:
                data = await handler.handle_authors(session, new_author)
                self.assertEqual(data[0].name, "new_author")

    async def test_handle_authors_new(self):
        new_author = ["new_author", "test_author"]
        async with self.session.get_session() as session:
            for handler in self.handler:
                data = await handler.handle_authors(session, new_author)
                self.assertEqual(len(data), 2)
                self.assertEqual(data[0].name, "test_author")

    async def test_handle_authors_empty(self):
        new_author = []
        async with self.session.get_session() as session:
            for handler in self.handler:
                data = await handler.handle_authors(session, new_author)
                self.assertEqual(len(data), 0)
                self.assertEqual(data, [])


class TestPublisher(AbstractTestDatabase,unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.publishers = [
            Publisher(name="test_publisher"),
            Publisher(name="test_publisher2"),
        ]
        async with self.session.get_session() as session:
            session.add_all(self.publishers)
            await session.commit()
        self.handler = DBWriter(self.session, OriconWeeklyScraper)


    async def test_handle_publishers_single_new(self):
        new_publishers = ["new_publisher"]
        async with self.session.get_session() as session:
            data = await self.handler.handle_publisher(session, new_publishers)
            self.assertEqual(data[0].name, "new_publisher")

    async def test_handle_publishers_new(self):
        new_publishers = ["new_publisher", "test_publisher"]
        async with self.session.get_session() as session:
            data = await self.handler.handle_publisher(session, new_publishers)
            self.assertEqual(len(data), 2)
            self.assertEqual(data[0].name, "test_publisher")

    async def test_handle_publishers_empty(self):
        new_publishers = []
        async with self.session.get_session() as session:
            data = await self.handler.handle_publisher(session, new_publishers)
            self.assertEqual(len(data), 0)
            self.assertEqual(data, [])


class TestTitle(AbstractTestDatabase,unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.titles = [Title(name="test_title"), Title(name="test_title2")]
        async with self.session.get_session() as session:
            session.add_all(self.titles)
            await session.commit()
        self.handler = DBWriter(self.session, OriconWeeklyScraper)


    async def test_handle_new_title(self):
        new_title = "new_title"
        async with self.session.get_session() as session:
            data = await self.handler.handle_title(session, new_title)
        self.assertEqual(data.name, "new_title")

    async def test_handle_old_title(self):
        new_title = "test_title"
        async with self.session.get_session() as session:
            data = await self.handler.handle_title(session, new_title)
            self.assertEqual(data.name, "test_title")
            await session.commit()
            items = await Title.get_all(session)
            self.assertEqual(len(items), 2)


class TestDate(AbstractTestDatabase,unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.handler = DBWriter(self.session, OriconWeeklyScraper)
        self.weeks = [
            Week(date=datetime.date(2022, 9, 11)),
            Week(date=datetime.date(2021, 8, 22)),
        ]


    @patch(
        "manga_sales.data_scraping.web_scraper.OriconWeeklyScraper.find_latest_date",
        return_value=datetime.date(2022, 9, 17),
    )
    async def test_get_date_if_exist(self, mock):
        async with self.session.get_session() as session:
            session.add_all(self.weeks)
            await session.commit()
            data = await self.handler.get_date(session)
            self.assertEqual(data, datetime.date(2022, 9, 17))

    @patch(
        "manga_sales.data_scraping.web_scraper.OriconWeeklyScraper.find_latest_date",
        side_effect=[datetime.date(2022, 9, 17), datetime.date(2022, 9, 24)],
    )
    async def test_get_date_recursion(self, mock):
        async with self.session.get_session() as session:
            session.add(Week(date=datetime.date(2022, 9, 17)))
            await session.commit()
            data = await self.handler.get_date(session)
            self.assertEqual(data, datetime.date(2022, 9, 24))


class TestWrite(AbstractTestDatabase,unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.weeks = [
            Week(date=datetime.date(2022, 9, 11)),
            Week(date=datetime.date(2021, 8, 22)),
        ]
        self.authors = [Author(name="test_author"), Author(name="test_author2")]
        self.publishers = [
            Publisher(name="test_publisher"),
            Publisher(name="test_publisher2"),
        ]
        async with self.session.get_session() as session:
            session.add_all(self.authors)
            session.add_all(self.publishers)
            session.add_all(self.weeks)
            await session.commit()
        self.handler = DBWriter(self.session, OriconWeeklyScraper)


    @patch(
        "manga_sales.data_scraping.db_handle.DBWriter.get_date",
        side_effect=[datetime.date(2022, 9, 13), None],
    )
    @patch(
        "manga_sales.data_scraping.web_scraper.OriconWeeklyScraper.get_data",
        return_value=[
            Content(
                name="title",
                volume=122,
                image="image name",
                authors=["test_author"],
                publisher=[],
                release_date=datetime.date(2022, 8, 11),
                rating=1,
                sold=13,
            ),
            Content(
                name="title2",
                volume=111,
                image="image name1",
                authors=["test_author2"],
                publisher=["test_publisher"],
                release_date=datetime.date(2022, 8, 21),
                rating=2,
                sold=22,
            ),
        ],
    )
    async def test_wrtire_success(self, mock_data, mock_date):
        await self.handler.write_data()
        async with self.session.get_session() as session:
            items = await Item.get_count(session)
            self.assertEqual(items, 2)
            authors = await Author.get_all(session)
            self.assertEqual(len(authors), 2)
