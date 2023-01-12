import pytest
from manga_sales.db.data_access_layers.author import AuthorDAO
from manga_sales.db.data_access_layers.item import ItemDAO
from manga_sales.db.data_access_layers.publisher import PublisherDAO
from manga_sales.db.data_access_layers.source import SourceDAO
from manga_sales.db.data_access_layers.source_type import SourceTypeDAO
from manga_sales.db.data_access_layers.title import TitleDAO
from manga_sales.db.data_access_layers.week import WeekDAO
from manga_sales.db.models import PreviousRank, Title
import datetime
from manga_sales.test.conftest import *


@pytest.mark.usefixtures("create_data")
class TestSource:
    @pytest.mark.parametrize("dao", [SourceDAO])
    async def test_source_get_all(self, dao_session):
        data = await dao_session.get_all()
        assert len(data) == 2


@pytest.mark.usefixtures("create_data")
class TestSourceType:
    @pytest.mark.parametrize("dao", [SourceTypeDAO])
    async def test_sourcetype_get_success(self, dao_session):
        data = await dao_session.get(pytest.sources[0].name)
        assert all(isinstance(x, SourceType) for x in data)
        assert data[0].id == pytest.source_types[0].id

    @pytest.mark.parametrize("dao", [SourceTypeDAO])
    async def test_sourcetype_get_none(self, dao_session):
        data = await dao_session.get("something wrong")
        assert data == None

    @pytest.mark.parametrize("dao", [SourceTypeDAO])
    async def test_sourcetype_get_by_source_success(self, dao_session):
        data = await dao_session.get_by_source(
            pytest.sources[0].name, pytest.source_types[0].type
        )
        assert data.id == pytest.source_types[0].id
        data2 = await dao_session.get_by_source(
            pytest.sources[1].name, pytest.source_types[0].type
        )
        assert data2.id == pytest.source_types[1].id

    @pytest.mark.parametrize("dao", [SourceTypeDAO])
    async def test_sourcetype_get_by_source_none(self, dao_session):
        data3 = await dao_session.get_by_source(
            "Something", pytest.source_types[0].type
        )
        assert data3 == None


@pytest.mark.usefixtures("create_data")
class TestWeek:
    @pytest.mark.parametrize("dao", [WeekDAO])
    async def test_all_group_success(self, dao_session) -> None:
        data = await dao_session.get_all_groupby(
            pytest.sources[0].name, pytest.source_types[0].type
        )
        assert data == [
            {"2021": {"August": [22]}},
            {"2022": {"September": [11]}},
        ]

    @pytest.mark.parametrize("dao", [WeekDAO])
    async def test_all_group_fail(self, dao_session) -> None:
        with pytest.raises(AssertionError):
            await dao_session.get_all_groupby(pytest.sources[0].name, "wrong")

    @pytest.mark.parametrize("dao", [WeekDAO])
    async def test_get_all_success(self, dao_session):
        data = await dao_session.get_all()
        assert len(data) == 2

    @pytest.mark.parametrize("dao", [WeekDAO])
    async def test_get_success(self, dao_session):
        data = await dao_session.get(pytest.weeks[0].date)
        assert data[0].date == pytest.weeks[0].date

    @pytest.mark.parametrize("dao", [WeekDAO])
    async def test_get_fail(self, dao_session):
        data = await dao_session.get(datetime.date(2022, 9, 12))
        assert data == None

    @pytest.mark.parametrize("dao", [WeekDAO])
    async def test_get_previous_row_success(self, dao_session):
        data = await dao_session.get_previous_week(
            pytest.weeks[0], pytest.source_types[0]
        )
        assert pytest.weeks[1].id == data.id

    @pytest.mark.parametrize("dao", [WeekDAO])
    async def test_get_previous_row_none(self, dao_session):
        data2 = await dao_session.get_previous_week(
            pytest.weeks[1], pytest.source_types[0]
        )
        assert data2 == None


@pytest.mark.usefixtures("create_data")
class TestItem:
    @pytest.mark.parametrize("dao", [ItemDAO])
    async def test_get_items_success(self, dao_session):
        data = await dao_session.get_instance("2022-09-11")
        assert len(data) == 1
        assert data[0].rating == 1

    @pytest.mark.parametrize("dao", [ItemDAO])
    async def test_get_items_empty(self, dao_session):
        data = await dao_session.get_instance("2022-09-12")
        assert len(data) == 0

    @pytest.mark.parametrize("dao", [ItemDAO])
    async def test_get_items_wrong_date_type(self, dao_session):
        with pytest.raises(TypeError):
            await dao_session.get_instance(datetime.date(2022, 9, 11))

    @pytest.mark.parametrize("dao", [ItemDAO])
    async def test_get_prev_rank_succes(self, dao_session):
        result = await dao_session.get_previous_rank(
            pytest.weeks[1],
            pytest.items[0].rating,
            pytest.items[0].title.name,
        )
        assert result == PreviousRank.UP.name

    @pytest.mark.parametrize("dao", [ItemDAO])
    async def test_get_prev_rank_none(self, dao_session):
        title = Title(name="test_none")
        pytest.items[0].title = title
        dao_session.session.add(title)
        await dao_session.session.commit()
        result = await dao_session.get_previous_rank(
            pytest.weeks[1],
            pytest.items[0].rating,
            pytest.items[0].title.name,
        )
        assert result == None


@pytest.mark.usefixtures("create_data")
class TestTitle:
    @pytest.mark.parametrize("dao", [TitleDAO])
    async def test_filter(self, dao_session):
        data = await dao_session.filter_by_name("test_title")
        assert data
        assert data.name == pytest.titles[0].name


@pytest.mark.usefixtures("create_data")
class TestAuthor:
    @pytest.mark.parametrize("dao", [AuthorDAO])
    async def test_filter(self, dao_session):
        data = await dao_session.filter_by_name([pytest.authors[0].name])
        assert data
        assert data[0].name == pytest.authors[0].name


@pytest.mark.usefixtures("create_data")
class TestPublisher:
    @pytest.mark.parametrize("dao", [PublisherDAO])
    async def test_filter(self, dao_session):
        data = await dao_session.filter_by_name([pytest.publishers[0].name])
        assert data
        assert data[0].name == pytest.publishers[0].name
