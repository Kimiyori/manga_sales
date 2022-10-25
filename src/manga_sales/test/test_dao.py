import pytest
from src.manga_sales.db.data_access_layers.author import AuthorDAO
from src.manga_sales.db.data_access_layers.item import ItemDAO
from src.manga_sales.db.data_access_layers.publisher import PublisherDAO
from src.manga_sales.db.data_access_layers.source import SourceDAO
from src.manga_sales.db.data_access_layers.source_type import SourceTypeDAO
from src.manga_sales.db.data_access_layers.title import TitleDAO
from src.manga_sales.db.data_access_layers.week import WeekDAO
from src.manga_sales.db.models import (
    Author,
    Item,
    Publisher,
    Source,
    SourceType,
    Title,
    Week,
)
import datetime
from src.manga_sales.test.conftest import *

class TestSource:
    @pytest_asyncio.fixture(scope="class", autouse=True)
    async def source_data(self, class_session_factory) -> None:
        async with class_session_factory() as session:
            self.__class__.sources = [Source(name="Oricon"), Source(name="Shoseki")]
            session.add_all(self.__class__.sources)
            await session.commit()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("dao", [SourceDAO])
    async def test_source_get_all(self, dao_session):
        data = await dao_session.get_all()
        assert len(data) == 2

class TestSourceType:
    @pytest_asyncio.fixture(scope="class", autouse=True)
    async def type_data(self, class_session_factory) -> None:
        async with class_session_factory() as session:
            self.__class__.sources = [Source(name="Oricon"), Source(name="Shoseki")]
            self.__class__.source_types = [
                SourceType(type="Weekly"),
                SourceType(type="Weekly"),
            ]
            for x in range(2):
                self.__class__.source_types[x].source = self.__class__.sources[x]
            session.add_all(self.__class__.sources)
            session.add_all(self.__class__.source_types)
            await session.commit()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("dao", [SourceTypeDAO])
    async def test_sourcetype_get_by_source_success(self, dao_session):
        data = await dao_session.get_by_source(
            self.__class__.sources[0].name, self.__class__.source_types[0].type
        )
        assert data.id == self.__class__.source_types[0].id
        data2 = await dao_session.get_by_source(
            self.__class__.sources[1].name, self.__class__.source_types[0].type
        )
        assert data2.id == self.__class__.source_types[1].id
        data3 = await dao_session.get_by_source(
            "Something", self.__class__.source_types[0].type
        )
        assert data3 == None


class TestWeek:
    @pytest_asyncio.fixture(scope="class", autouse=True)
    async def week_data(self, class_session_factory) -> None:
        async with class_session_factory() as session:
            self.__class__.source = Source(name="Oricon")
            self.__class__.source_type = SourceType(type="Weekly")
            self.__class__.source_type.source = self.__class__.source
            self.__class__.weeks = [
                Week(date=datetime.date(2022, 9, 11)),
                Week(date=datetime.date(2022, 6, 6)),
                Week(date=datetime.date(2021, 8, 22)),
            ]
            for x in self.weeks:
                x.source_type = self.__class__.source_type
                session.add(self.__class__.source)
                session.add(self.__class__.source_type)
                session.add_all(self.weeks)
            await session.commit()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("dao", [WeekDAO])
    async def test_all_group(self, dao_session) -> None:
        data = await dao_session.get_all_groupby(
            self.__class__.source.name, self.__class__.source_type.type
        )
        assert data == [
            {"2021": {"August": [22]}},
            {"2022": {"June": [6], "September": [11]}},
        ]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("dao", [WeekDAO])
    async def test_get_all(self, dao_session):
        data = await dao_session.get_all()
        assert len(data) == 3

    @pytest.mark.asyncio
    @pytest.mark.parametrize("dao", [WeekDAO])
    async def test_get(self, dao_session):
        data = await dao_session.get(datetime.date(2022, 9, 11))
        assert data[0].date == self.__class__.weeks[0].date

    @pytest.mark.asyncio
    @pytest.mark.parametrize("dao", [WeekDAO])
    async def test_get_last_row(self, dao_session):
        data = await dao_session.get(datetime.date(2022, 9, 11))
        assert data[0].date == self.__class__.weeks[0].date

    @pytest.mark.asyncio
    @pytest.mark.parametrize("dao", [WeekDAO])
    async def test_get_previous_row_success(self, dao_session):
        data = await dao_session.get_previous_week(
            self.__class__.weeks[0], self.__class__.source_type
        )
        assert self.weeks[1].id == data.id
        data2 = await dao_session.get_previous_week(
            self.__class__.weeks[2], self.__class__.source_type
        )
        assert data2 == None


class TestItem:
    @pytest_asyncio.fixture(scope="class", autouse=True)
    async def item_data(self, class_session_factory) -> None:
        self.__class__.weeks = [
            Week(date=datetime.date(2022, 9, 11)),
            Week(date=datetime.date(2021, 8, 22)),
        ]
        self.__class__.authors = [
            Author(name="test_author"),
            Author(name="test_author2"),
        ]
        self.__class__.publishers = [
            Publisher(name="test_publisher"),
            Publisher(name="test_publisher2"),
        ]
        self.__class__.titles = [Title(name="test_title")]
        self.__class__.items = [
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
        async with class_session_factory() as session:
            for i, item in enumerate(self.items):
                item.title = self.__class__.titles[0]
                item.author.append(self.__class__.authors[i])
                item.publisher.append(self.__class__.publishers[i])
            for i, week in enumerate(self.__class__.weeks):
                week.items.append(self.__class__.items[i])
            session.add_all(self.__class__.weeks)
            await session.commit()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("dao", [ItemDAO])
    async def test_get_items_success(self, dao_session):
        data = await dao_session.get_instance("2022-09-11")
        assert len(data) == 1
        assert data[0].rating == 1

    @pytest.mark.asyncio
    @pytest.mark.parametrize("dao", [ItemDAO])
    async def test_get_items_empty(self, dao_session):
        data = await dao_session.get_instance("2022-09-12")
        assert len(data) == 0

    @pytest.mark.asyncio
    @pytest.mark.parametrize("dao", [ItemDAO])
    async def test_get_items_wrong_date_type(self, dao_session):
        with pytest.raises(TypeError):
            await dao_session.get_instance(datetime.date(2022, 9, 11))

    @pytest.mark.asyncio
    @pytest.mark.parametrize("dao", [ItemDAO])
    async def test_get_prev_rank_succes(self, dao_session):
        result = await dao_session.get_previous_rank(
            self.__class__.weeks[1],
            self.__class__.items[0].rating,
            self.__class__.items[0].title.name,
        )
        assert result.rank == 2

    @pytest.mark.asyncio
    @pytest.mark.parametrize("dao", [ItemDAO])
    async def test_get_prev_rank_none(self, dao_session):
        title = Title(name="test_none")
        self.items[0].title = title
        dao_session.session.add(title)
        await dao_session.session.commit()
        result = await dao_session.get_previous_rank(
            self.__class__.weeks[1],
            self.__class__.items[0].rating,
            self.__class__.items[0].title.name,
        )
        assert result == None


class TestTitle:
    @pytest_asyncio.fixture(scope="class", autouse=True)
    async def title_data(self, class_session_factory) -> None:
        self.__class__.titles = [Title(name="test_title"), Title(name="test_title2")]
        async with class_session_factory() as session:
            session.add_all(self.__class__.titles)
            await session.commit()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("dao", [TitleDAO])
    async def test_filter(self, dao_session):
        data = await dao_session.filter_by_name("test_title")
        assert data
        assert data.name == self.__class__.titles[0].name


class TestAuthor:
    @pytest_asyncio.fixture(scope="class", autouse=True)
    async def author_data(self, class_session_factory) -> None:
        self.__class__.authors = [
            Author(name="test_author"),
            Author(name="test_author2"),
        ]
        async with class_session_factory() as session:
            session.add_all(self.__class__.authors)
            await session.commit()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("dao", [AuthorDAO])
    async def test_filter(self, dao_session):
        data = await dao_session.filter_by_name([self.__class__.authors[0].name])
        assert data
        assert data[0].name == self.__class__.authors[0].name


class TestPublisher:
    @pytest_asyncio.fixture(scope="class", autouse=True)
    async def publisher_data(self, class_session_factory) -> None:
        self.__class__.publishers = [
            Publisher(name="test_publisher"),
            Publisher(name="test_publisher2"),
        ]
        async with class_session_factory() as session:
            session.add_all(self.__class__.publishers)
            await session.commit()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("dao", [PublisherDAO])
    async def test_filter(self, dao_session):
        data = await dao_session.filter_by_name([self.__class__.publishers[0].name])
        assert data
        assert data[0].name == self.__class__.publishers[0].name
