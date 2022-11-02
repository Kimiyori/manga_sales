from unittest import mock
import pytest
from .conftest import manga_updates_container, manga_updates_list, manga_updates_title


@pytest.mark.asyncio
@mock.patch("src.data_scraping.meta.AbstractBase.fetch")
async def test_get_page_all_success(
    mock, manga_updates_container, manga_updates_list, manga_updates_title
):
    mock.side_effect = [manga_updates_list, manga_updates_title]
    async with manga_updates_container(title="Dawn Aria") as session:
        authors = session.get_authors()
        assert authors == ["AKAISHI Michiyo"]
        publishers = session.get_publishers()
        assert publishers == ["Shogakukan"]
        title = session.get_title()
        assert title == "Akatsuki no Aria"


@pytest.mark.asyncio
@mock.patch("src.data_scraping.meta.AbstractBase.fetch")
async def test_get_title_exception(
    mock, manga_updates_container, manga_updates_list, manga_updates_title
):
    manga_updates_title.find("span", {"class": "releasestitle tabletitle"})[
        "class"
    ] = "foo"
    mock.side_effect = [manga_updates_list, manga_updates_title]
    async with manga_updates_container(title="Dawn Aria") as session:
        title = session.get_title()
        assert title == "Dawn Aria"


@pytest.mark.asyncio
@mock.patch("src.data_scraping.meta.AbstractBase.fetch")
async def test_get_authors_error(
    mock, manga_updates_container, manga_updates_list, manga_updates_title
):
    manga_updates_title.find("b", string="Author(s)").replace_with("something")
    mock.side_effect = [manga_updates_list, manga_updates_title]
    async with manga_updates_container(title="Dawn Aria") as session:
        authors = session.get_authors()
        assert authors == []


@pytest.mark.asyncio
@mock.patch("src.data_scraping.meta.AbstractBase.fetch")
async def test_get_publishers_error(
    mock, manga_updates_container, manga_updates_list, manga_updates_title
):
    manga_updates_title.find("b", string="Original Publisher").replace_with("something")
    mock.side_effect = [manga_updates_list, manga_updates_title]
    async with manga_updates_container(title="Dawn Aria") as session:
        publishers = session.get_publishers()
        assert publishers == []


@pytest.mark.asyncio
@mock.patch("src.data_scraping.meta.AbstractBase.fetch")
async def test_get_most_similar_title_empty_items(
    mock, manga_updates_container, manga_updates_list, manga_updates_title
):
    lst = manga_updates_list.find_all("div", {"class": "col-12 col-lg-6 p-3 text"})
    for x in lst:
        x["class"] = "something"
    mock.side_effect = [manga_updates_list, manga_updates_title]
    with pytest.raises(AssertionError):
        async with manga_updates_container(title="Dawn Aria"):
            pass


@pytest.mark.asyncio
@mock.patch("src.data_scraping.meta.AbstractBase.fetch")
async def test_get_most_similar_title_empty_titles(
    mock, manga_updates_container, manga_updates_list, manga_updates_title
):
    lst = manga_updates_list.find_all("div", {"class": "col-12 col-lg-6 p-3 text"})
    for x in lst:
        y = x.find_all("div", {"class": "text"})
        for z in y:
            z["class"] = "not_text"
    mock.side_effect = [manga_updates_list, manga_updates_title]
    with pytest.raises(AssertionError):
        async with manga_updates_container(title="Dawn Aria"):
            pass


@pytest.mark.asyncio
@mock.patch("src.data_scraping.meta.AbstractBase.fetch")
async def test_get_image_success(
    mock, manga_updates_container, manga_updates_list, manga_updates_title
):
    mock.side_effect = [
        manga_updates_list,
        manga_updates_title,
        bytes("image", "utf-8"),
    ]
    async with manga_updates_container(title="Dawn Aria") as session:
        res = await session.get_image()
        assert isinstance(res, bytes)


@pytest.mark.asyncio
@mock.patch("src.data_scraping.meta.AbstractBase.fetch")
async def test_get_image__nof_found_img(
    mock, manga_updates_container, manga_updates_list, manga_updates_title
):
    manga_updates_title.find("img", {"class": "img-fluid"})["class"] = "sss"
    mock.side_effect = [
        manga_updates_list,
        manga_updates_title,
        bytes("image", "utf-8"),
    ]
    async with manga_updates_container(title="Dawn Aria") as session:
        res = await session.get_image()
        assert res is None
