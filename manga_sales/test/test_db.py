import unittest
from manga_sales.data_scraping.exceptions import IncorrectMethod, NotFound, Unsuccessful
from manga_sales.data_scraping.session_context_manager import Session
from manga_sales.main import app
from manga_sales.db import AsyncDatabaseSession
from manga_sales.models import Author, Item, Publisher, Title, Week
from manga_sales.settings import config
import datetime


class TestWeek(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await app["db"].create_db()
        self.session = AsyncDatabaseSession(app["config"]["postgres_test"])
        self.session.init(False)
        await self.session.create_all()
        self.weeks = [
            Week(date=datetime.date(2022, 9, 11)),
            Week(date=datetime.date(2022, 6, 6)),
            Week(date=datetime.date(2021, 8, 22)),
        ]
        async with self.session.get_session as session:
            session.add_all(self.weeks)
            await session.commit()

    async def asyncTearDown(self):
        await app["db"].delete_db()

    async def test_all_group(self):
        async with self.session.get_session as session:
            data = await Week.get_all_groupby(session)
            self.assertEqual(
                data,
                [
                    {"2021": {"August": ["2021-08-22"]}},
                    {"2022": {"June": ["2022-06-06"], "September": ["2022-09-11"]}},
                ],
            )

    async def test_get_all(self):
        async with self.session.get_session as session:
            data = await Week.get_all(session)
            self.assertEqual(len(data), 3)

    async def test_get(self):
        async with self.session.get_session as session:
            data = await Week.get(session, datetime.date(2022, 9, 11))
            self.assertEqual(data[0].date, self.weeks[0].date)

    async def test_get_last_row(self):
        async with self.session.get_session as session:
            data = await Week.get(session, datetime.date(2022, 9, 11))
            self.assertEqual(data[0].date, self.weeks[0].date)


class TestItem(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await app["db"].create_db()
        self.session = AsyncDatabaseSession(app["config"]["postgres_test"])
        self.session.init(False)
        await self.session.create_all()
        self.weeks = [
            Week(date=datetime.date(2022, 9, 11)),
            Week(date=datetime.date(2021, 8, 22)),
        ]
        self.authors = [Author(name="test_author"), Author(name="test_author2")]
        self.publishers = [
            Publisher(name="test_publisher"),
            Publisher(name="test_publisher2"),
        ]
        self.titles = [Title(name="test_title"), Title(name="test_title2")]
        self.items = [
            Item(
                rating=1,
                volume=22,
                release_date=datetime.date(2022, 8, 11),
                sold=11.434,
                image="2022-08-11/test.jpg",
            ),
            Item(
                rating=2,
                volume=13,
                release_date=datetime.date(2022, 8, 25),
                sold=5.234,
                image="2022-08-11/test2.jpg",
            ),
        ]
        async with self.session.get_session as session:
            for i, item in enumerate(self.items):
                item.title = self.titles[i]
                item.author.append(self.authors[i])
                item.publisher.append(self.publishers[i])
            for i, week in enumerate(self.weeks):
                week.items.append(self.items[i])
            session.add_all(self.weeks)
            await session.commit()

    async def asyncTearDown(self):
        await app["db"].delete_db()

    async def test_get_items_success(self):
        async with self.session.get_session as session:
            data = await Item.get_instance(session, "2022-09-11")
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0].rating, 1)

    async def test_get_items_empty(self):
        async with self.session.get_session as session:
            data = await Item.get_instance(session, "2022-09-12")
            self.assertEqual(len(data), 0)

    async def test_get_items_wrong_date_type(self):
        async with self.session.get_session as session:
            with self.assertRaises(TypeError):
                await Item.get_instance(session, datetime.date(2022, 9, 11))


class TestTitle(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await app["db"].create_db()
        self.session = AsyncDatabaseSession(app["config"]["postgres_test"])
        self.session.init(False)
        await self.session.create_all()
        self.titles = [Title(name="test_title"), Title(name="test_title2")]
        async with self.session.get_session as session:
            session.add_all(self.titles)
            await session.commit()

    async def asyncTearDown(self):
        await app["db"].delete_db()

    async def test_filter(self):
        async with self.session.get_session as session:
            data = await Title.filter_by_name(session, "test_title")
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0].name, "test_title")


class TestAuthors(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await app["db"].create_db()
        self.session = AsyncDatabaseSession(app["config"]["postgres_test"])
        self.session.init(False)
        await self.session.create_all()
        self.authors = [Author(name="test_author"), Author(name="test_author2")]
        async with self.session.get_session as session:
            session.add_all(self.authors)
            await session.commit()

    async def asyncTearDown(self):
        await app["db"].delete_db()

    async def test_filter(self):
        async with self.session.get_session as session:
            data = await Author.filter_by_name(session, ["test_author"])
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0][0].name, "test_author")


class TestPublishers(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await app["db"].create_db()
        self.session = AsyncDatabaseSession(app["config"]["postgres_test"])
        self.session.init(False)
        await self.session.create_all()
        self.publishers = [
            Publisher(name="test_publisher"),
            Publisher(name="test_publisher2"),
        ]
        async with self.session.get_session as session:
            session.add_all(self.publishers)
            await session.commit()

    async def asyncTearDown(self):
        await app["db"].delete_db()

    async def test_filter(self):
        async with self.session.get_session as session:
            data = await Publisher.filter_by_name(session, ["test_publisher"])
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0][0].name, "test_publisher")
