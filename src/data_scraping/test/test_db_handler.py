import unittest
from unittest.mock import patch
from src.data_scraping.dataclasses import Content
from src.data_scraping.db_handle import DBWriter
from src.data_scraping.web_scraper import (
    OriconWeeklyScraper,
    ShosekiWeeklyScraper,
)
from src.test.test_db import AbstractTestDatabase
from src.manga_sales.db.models import (
    Author,
    Item,
    PreviousRank,
    Publisher,
    Source,
    SourceType,
    Title,
    Week,
)
import datetime


class TestAuthors(AbstractTestDatabase, unittest.IsolatedAsyncioTestCase):
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


class TestPublisher(AbstractTestDatabase, unittest.IsolatedAsyncioTestCase):
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


class TestTitle(AbstractTestDatabase, unittest.IsolatedAsyncioTestCase):
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


class TestDate(AbstractTestDatabase, unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.handler = DBWriter(self.session, OriconWeeklyScraper)
        self.source = Source(name="Oricon")
        self.source_type = [SourceType(type="Weekly")]
        self.weeks = [
            Week(date=datetime.date(2022, 9, 11)),
            Week(date=datetime.date(2021, 8, 22)),
        ]
        for x in self.source_type:
            x.source = self.source
        for x in self.weeks:
            x.source_type = self.source_type[0]

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
        side_effect=[datetime.date(2022, 9, 18), datetime.date(2022, 9, 19)],
    )
    async def test_get_date_recursion(self, mock):
        async with self.session.get_session() as session:
            session.add(self.source)
            session.add_all(self.source_type)
            session.add_all(self.weeks)
            await session.commit()
            data = await self.handler.get_date(session)
            self.assertEqual(data, datetime.date(2022, 9, 18))


class TestWrite(AbstractTestDatabase, unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.source = [Source(name="Oricon"), Source(name="Shoseki")]
        self.source_type = [SourceType(type="Weekly"), SourceType(type="Weekly")]
        self.weeks = [
            Week(date=datetime.date(2021, 8, 22)),
            Week(date=datetime.date(2022, 9, 11)),
        ]
        self.authors = [Author(name="test_author"), Author(name="test_author2")]
        self.publishers = [
            Publisher(name="test_publisher"),
            Publisher(name="test_publisher2"),
        ]
        self.titles = [Title(name="test_title")]
        self.items = [
            Item(
                rating=2,
                volume=22,
                release_date=datetime.date(2022, 8, 11),
                sold=11.434,
                image="2022-08-11/test.jpg",
            ),
            Item(
                rating=1,
                volume=13,
                release_date=datetime.date(2022, 8, 25),
                sold=5.234,
                image="2022-08-11/test2.jpg",
            ),
        ]
        async with self.session.get_session() as session:
            self.source_type[0].source = self.source[0]
            for x in self.weeks:
                x.source_type = self.source_type[0]
            for i, item in enumerate(self.items):
                item.title = self.titles[0]
                item.week = self.weeks[1]
            session.add(self.titles[0])
            session.add_all(self.items)
            session.add_all(self.source)
            session.add_all(self.source_type)
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
                name="test_title",
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
            self.assertEqual(items, 4)
            authors = await Author.get_all(session)
            self.assertEqual(len(authors), 2)
            new_items = await Item.get(session, volume=122)
            self.assertEqual(new_items[0].previous_rank, PreviousRank.SAME)

    async def test_get_previous_week(self):
        async with self.session.get_session() as session:
            week = Week(date=datetime.date(2022, 9, 20))
            res = await self.handler.get_previous_week(
                session, week, self.source_type[0]
            )
            self.assertEqual(res.date, self.weeks[1].date)
