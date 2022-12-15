import datetime
import random
from unittest import mock
from src.manga_scrapers.database_handler import DatabaseConnector
from src.manga_scrapers.dataclasses import Content
from src.manga_scrapers.test.conftest import (
    oricon_container,
    db_session_container,
    create_data_scraper,
)
import pytest

from src.manga_sales.db.models import Author, Item, PreviousRank, Publisher, Week


@pytest.mark.usefixtures("create_data_scraper")
class TestDatabaseSaver:
    @mock.patch(
        "src.data_scraping.main_scrapers.oricon_scraper.OriconWeeklyScraper.get_data"
    )
    async def test_insert_data(
        self, mock, db_session_container, oricon_container, faker
    ):
        dte = datetime.date(2022, 11, 11)
        contents = []
        for x in range(1, 31):
            contents.append(
                Content(
                    name=faker.pystr(max_chars=40),
                    volume=faker.pyint(),
                    image=faker.pystr(max_chars=40, suffix=".jpg"),
                    authors=[faker.name() for _ in range(3)],
                    publishers=[faker.name() for _ in range(3)],
                    rating=x,
                    release_date=faker.date_this_century(),
                    sales=faker.pyint(min_value=1_000, max_value=200_000),
                )
            )
        mock.return_value = contents
        cont = DatabaseConnector(oricon_container)
        await cont.insert_data(dte)
        items = db_session_container.item()
        res = await items.get_instance(dte.strftime("%Y-%m-%d"))
        assert len(res) == 30
        for item, content in zip(res, contents):
            assert item.id == content.rating
            assert item.title == content.name
            assert item.rating == content.rating
            assert item.volume == content.volume
            assert item.image == content.image
            assert item.sold == content.sales
            assert item.release_date == content.release_date
            assert sorted(item.authors) == sorted(content.authors)
            assert sorted(item.publishers) == sorted(content.publishers)

    @mock.patch(
        "src.data_scraping.main_scrapers.oricon_scraper.OriconWeeklyScraper.get_data"
    )
    async def test_insert_data_with_prev_week(
        self, mock, db_session_container, oricon_container, faker
    ):
        cont = DatabaseConnector(oricon_container)
        week = Week(
            date=datetime.date(2022, 11, 4), source_type_id=pytest.source_types[0].id
        )
        week_session = db_session_container.week()
        item_session = db_session_container.item()
        title = await cont.handle_title("test")
        item = Item(
            rating=1,
            volume=2,
            release_date=faker.date_this_century(),
            sold=faker.pyint(min_value=1_000, max_value=200_000),
            image=faker.pystr(max_chars=40, suffix=".jpg"),
        )
        item.title = title
        item_session.add(item)
        week.items.extend([item])
        week_session.add(week)
        session = db_session_container.session()
        await session.commit()

        dte = datetime.date(2022, 11, 11)
        contents = [
            Content(
                name="test",
                volume=3,
                image=faker.pystr(max_chars=40, suffix=".jpg"),
                rating=2,
                release_date=faker.date_this_century(),
                sales=faker.pyint(min_value=1_000, max_value=200_000),
                authors=[faker.name() for _ in range(3)],
                publishers=[faker.name() for _ in range(3)],
            )
        ]
        mock.return_value = contents
        await cont.insert_data(dte)
        items = db_session_container.item()
        res = await items.get_instance(dte.strftime("%Y-%m-%d"))
        count = await items.get_count()
        assert count == 2
        assert res[0].rating == 2
        assert res[0].previous_rank == PreviousRank.DOWN

    async def test_prev_week(self, db_session_container, oricon_container, faker):
        cont = DatabaseConnector(oricon_container)
        week = Week(
            date=datetime.date(2022, 11, 4), source_type_id=pytest.source_types[0].id
        )
        week_session = db_session_container.week()
        item_session = db_session_container.item()
        title = await cont.handle_title("test")
        item = Item(
            rating=1,
            volume=2,
            release_date=faker.date_this_century(),
            sold=faker.pyint(min_value=1_000, max_value=200_000),
            image=faker.pystr(max_chars=40, suffix=".jpg"),
        )
        item.title = title
        item_session.add(item)
        week.items.extend([item])
        week_session.add(week)
        session = db_session_container.session()
        await session.commit()
        res = await cont.get_previous_place(week, 1, "test")
        assert res == PreviousRank.SAME.name

    async def test_handle_authors(self, db_session_container, oricon_container):
        cont = DatabaseConnector(oricon_container)
        authors_session = db_session_container.authors()
        author = Author(name="test")
        authors_session.add(author)
        session = db_session_container.session()
        await session.commit()
        res = await cont.handle_authors(["test", "test2"])
        assert len(res) == 2
        assert res[0].name == "test"
        assert res[0].id == 1
        assert res[1].id == None

    async def test_handle_publishers(self, db_session_container, oricon_container):
        cont = DatabaseConnector(oricon_container)
        publishers_session = db_session_container.publishers()
        publisher = Publisher(name="test")
        publishers_session.add(publisher)
        session = db_session_container.session()
        await session.commit()
        res = await cont.handle_publishers(["test", "test2"])
        assert len(res) == 2
        assert res[0].name == "test"
        assert res[0].id == 1
        assert res[1].id == None
