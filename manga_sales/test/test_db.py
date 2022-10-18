import unittest
from manga_sales.settings import config
from manga_sales.db import AsyncTestDatabaseSession
from manga_sales.models import Author, Item, Publisher, Source, SourceType, Title, Week
import datetime


class AbstractTestDatabase:
    async def asyncSetUp(self) -> None:
        self.session = AsyncTestDatabaseSession(config["postgres_test"])
        await self.session.init()

    async def asyncTearDown(self) -> None:
        await self.session.delete_db()


class TestSourceType(AbstractTestDatabase, unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.sources = [Source(name="Oricon"), Source(name="Shoseki")]
        self.source_types = [SourceType(type="Weekly"), SourceType(type="Weekly")]
        for x in range(2):
            self.source_types[x].source = self.sources[x]
        async with self.session.get_session() as session:
            session.add_all(self.sources)
            session.add_all(self.source_types)
            await session.commit()

    async def test_get_by_source_success(self):
        async with self.session.get_session() as session:
            data = await SourceType.get_by_source(session, "Oricon", "Weekly")
            self.assertEqual(data.id, self.source_types[0].id)
            data2 = await SourceType.get_by_source(session, "Shoseki", "Weekly")
            self.assertEqual(data2.id, self.source_types[1].id)
            data3 = await SourceType.get_by_source(session, "Something", "Weekly")
            self.assertEqual(data3, None)


class TestWeek(AbstractTestDatabase, unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.source = Source(name="Oricon")
        self.source_type = SourceType(type="Weekly")
        self.source_type.source = self.source
        self.weeks = [
            Week(date=datetime.date(2022, 9, 11)),
            Week(date=datetime.date(2022, 6, 6)),
            Week(date=datetime.date(2021, 8, 22)),
        ]
        for x in self.weeks:
            x.source_type = self.source_type
        async with self.session.get_session() as session:
            session.add(self.source)
            session.add(self.source_type)
            session.add_all(self.weeks)
            await session.commit()

    async def test_all_group(self) -> None:
        async with self.session.get_session() as session:
            data = await Week.get_all_groupby(
                session, self.source.name, self.source_type.type
            )
            self.assertEqual(
                data,
                [
                    {"2021": {"August": [22]}},
                    {"2022": {"June": [6], "September": [11]}},
                ],
            )

    async def test_get_all(self):
        async with self.session.get_session() as session:
            data = await Week.get_all(session)
            self.assertEqual(len(data), 3)

    async def test_get(self):
        async with self.session.get_session() as session:
            data = await Week.get(session, datetime.date(2022, 9, 11))
            self.assertEqual(data[0].date, self.weeks[0].date)

    async def test_get_last_row(self):
        async with self.session.get_session() as session:
            data = await Week.get(session, datetime.date(2022, 9, 11))
            self.assertEqual(data[0].date, self.weeks[0].date)

    async def test_get_previous_row_success(self):
        async with self.session.get_session() as session:
            data = await Week.get_previous_week(
                session, self.weeks[0], self.source_type
            )
            self.assertEqual(self.weeks[1].id, data.id)
            data2 = await Week.get_previous_week(
                session, self.weeks[2], self.source_type
            )
            self.assertEqual(data2, None)


class TestItem(AbstractTestDatabase, unittest.IsolatedAsyncioTestCase):
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
        self.titles = [Title(name="test_title")]
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
        async with self.session.get_session() as session:
            for i, item in enumerate(self.items):
                item.title = self.titles[0]
                item.author.append(self.authors[i])
                item.publisher.append(self.publishers[i])
            for i, week in enumerate(self.weeks):
                week.items.append(self.items[i])
            session.add_all(self.weeks)
            await session.commit()

    async def test_get_items_success(self):
        async with self.session.get_session() as session:
            data = await Item.get_instance(session, "2022-09-11")
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0].rating, 1)

    async def test_get_items_empty(self):
        async with self.session.get_session() as session:
            data = await Item.get_instance(session, "2022-09-12")
            self.assertEqual(len(data), 0)

    async def test_get_items_wrong_date_type(self):
        async with self.session.get_session() as session:
            with self.assertRaises(TypeError):
                await Item.get_instance(session, datetime.date(2022, 9, 11))

    async def test_get_prev_rank_succes(self):
        async with self.session.get_session() as session:
            result = await Item.get_previous_rank(
                session, self.weeks[1], self.items[0].rating, self.items[0].title.name
            )
            self.assertEqual(result.rank, 2)

    async def test_get_prev_rank_none(self):
        async with self.session.get_session() as session:
            title = Title(name="test_none")
            self.items[0].title = title
            session.add(title)
            await session.commit()
            result = await Item.get_previous_rank(
                session, self.weeks[1], self.items[0].rating, self.items[0].title.name
            )
            self.assertEqual(result, None)


class TestTitle(AbstractTestDatabase, unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.titles = [Title(name="test_title"), Title(name="test_title2")]
        async with self.session.get_session() as session:
            session.add_all(self.titles)
            await session.commit()

    async def test_filter(self):
        async with self.session.get_session() as session:
            data = await Title.filter_by_name(session, "test_title")
            self.assertTrue(data)
            self.assertEqual(data.name, "test_title")


class TestAuthors(AbstractTestDatabase, unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.authors = [Author(name="test_author"), Author(name="test_author2")]
        async with self.session.get_session() as session:
            session.add_all(self.authors)
            await session.commit()

    async def test_filter(self):
        async with self.session.get_session() as session:
            data = await Author.filter_by_name(session, ["test_author"])
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0].name, "test_author")


class TestPublishers(AbstractTestDatabase, unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.publishers = [
            Publisher(name="test_publisher"),
            Publisher(name="test_publisher2"),
        ]
        async with self.session.get_session() as session:
            session.add_all(self.publishers)
            await session.commit()

    async def test_filter(self):
        async with self.session.get_session() as session:
            data = await Publisher.filter_by_name(session, ["test_publisher"])
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0].name, "test_publisher")
