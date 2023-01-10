import pytest

from manga_scrapers.utils.url_handler import build_url
from manga_scrapers.test.conftest import (
    manga_updates_container,
    manga_updates_list,
    manga_updates_title,
    aioresponse,
)


@pytest.mark.asyncio
async def test_get_page_all_success(
    aioresponse, manga_updates_container, manga_updates_list, manga_updates_title
):
    aioresponse.get(
        build_url(
            scheme="https",
            netloc="www.mangaupdates.com",
            path=["series.html"],
            query={"type": "manga", "perpage": 5, "search": "Dawn Aria"},
        ),
        body=str(manga_updates_list),
    )
    aioresponse.get(
        "https://www.mangaupdates.com/series/ijystpf/akatsuki-no-aria",
        body=str(manga_updates_title),
    )
    async with manga_updates_container(title="Dawn Aria") as session:
        authors = session.get_authors()
        assert authors == ["AKAISHI Michiyo"]
        publishers = session.get_publishers()
        assert publishers == ["Shogakukan"]
        title = session.get_title()
        assert title == "Akatsuki no Aria"


@pytest.mark.asyncio
async def test_get_title_exception(
    aioresponse, manga_updates_container, manga_updates_list, manga_updates_title
):
    manga_updates_title.find("span", {"class": "releasestitle tabletitle"})[
        "class"
    ] = "foo"
    aioresponse.get(
        build_url(
            scheme="https",
            netloc="www.mangaupdates.com",
            path=["series.html"],
            query={"type": "manga", "perpage": 5, "search": "Dawn Aria"},
        ),
        body=str(manga_updates_list),
    )
    aioresponse.get(
        "https://www.mangaupdates.com/series/ijystpf/akatsuki-no-aria",
        body=str(manga_updates_title),
    )
    async with manga_updates_container(title="Dawn Aria") as session:
        title = session.get_title()
        assert title == "Dawn Aria"


@pytest.mark.asyncio
async def test_get_authors_error(
    aioresponse, manga_updates_container, manga_updates_list, manga_updates_title
):
    manga_updates_title.find("b", string="Author(s)").replace_with("something")
    aioresponse.get(
        build_url(
            scheme="https",
            netloc="www.mangaupdates.com",
            path=["series.html"],
            query={"type": "manga", "perpage": 5, "search": "Dawn Aria"},
        ),
        body=str(manga_updates_list),
    )
    aioresponse.get(
        "https://www.mangaupdates.com/series/ijystpf/akatsuki-no-aria",
        body=str(manga_updates_title),
    )
    async with manga_updates_container(title="Dawn Aria") as session:
        authors = session.get_authors()
        assert authors == []


@pytest.mark.asyncio
async def test_get_publishers_error(
    aioresponse, manga_updates_container, manga_updates_list, manga_updates_title
):
    manga_updates_title.find("b", string="Original Publisher").replace_with("something")
    aioresponse.get(
        build_url(
            scheme="https",
            netloc="www.mangaupdates.com",
            path=["series.html"],
            query={"type": "manga", "perpage": 5, "search": "Dawn Aria"},
        ),
        body=str(manga_updates_list),
    )
    aioresponse.get(
        "https://www.mangaupdates.com/series/ijystpf/akatsuki-no-aria",
        body=str(manga_updates_title),
    )
    async with manga_updates_container(title="Dawn Aria") as session:
        publishers = session.get_publishers()
        assert publishers == []


@pytest.mark.asyncio
async def test_get_most_similar_title_empty_items(
    aioresponse, manga_updates_container, manga_updates_list, manga_updates_title
):
    lst = manga_updates_list.find_all("div", {"class": "col-12 col-lg-6 p-3 text"})
    for x in lst:
        x["class"] = "something"
    aioresponse.get(
        build_url(
            scheme="https",
            netloc="www.mangaupdates.com",
            path=["series.html"],
            query={"type": "manga", "perpage": 5, "search": "Dawn Aria"},
        ),
        body=str(manga_updates_list),
    )
    aioresponse.get(
        "https://www.mangaupdates.com/series/ijystpf/akatsuki-no-aria",
        body=str(manga_updates_title),
    )
    with pytest.raises(AssertionError):
        async with manga_updates_container(title="Dawn Aria"):
            pass


@pytest.mark.asyncio
async def test_get_most_similar_title_empty_titles(
    aioresponse, manga_updates_container, manga_updates_list, manga_updates_title
):
    lst = manga_updates_list.find_all("div", {"class": "col-12 col-lg-6 p-3 text"})
    for x in lst:
        y = x.find_all("div", {"class": "text"})
        for z in y:
            z["class"] = "not_text"
    aioresponse.get(
        build_url(
            scheme="https",
            netloc="www.mangaupdates.com",
            path=["series.html"],
            query={"type": "manga", "perpage": 5, "search": "Dawn Aria"},
        ),
        body=str(manga_updates_list),
    )
    aioresponse.get(
        "https://www.mangaupdates.com/series/ijystpf/akatsuki-no-aria",
        body=str(manga_updates_title),
    )
    with pytest.raises(AssertionError):
        async with manga_updates_container(title="Dawn Aria"):
            pass


@pytest.mark.asyncio
async def test_get_image_success(
    aioresponse, manga_updates_container, manga_updates_list, manga_updates_title
):
    aioresponse.get(
        build_url(
            scheme="https",
            netloc="www.mangaupdates.com",
            path=["series.html"],
            query={"type": "manga", "perpage": 5, "search": "Dawn Aria"},
        ),
        body=str(manga_updates_list),
    )
    aioresponse.get(
        "https://www.mangaupdates.com/series/ijystpf/akatsuki-no-aria",
        body=str(manga_updates_title),
    )
    aioresponse.get(
        "https://cdn.mangaupdates.com/image/i128641.png",
        body=bytes("img", "utf-8"),
    )
    async with manga_updates_container(title="Dawn Aria") as session:
        res = await session.get_image()
        assert isinstance(res, bytes)


@pytest.mark.asyncio
async def test_get_image__nof_found_img(
    aioresponse, manga_updates_container, manga_updates_list, manga_updates_title
):
    manga_updates_title.find("img", {"class": "img-fluid"})["class"] = "sss"
    aioresponse.get(
        build_url(
            scheme="https",
            netloc="www.mangaupdates.com",
            path=["series.html"],
            query={"type": "manga", "perpage": 5, "search": "Dawn Aria"},
        ),
        body=str(manga_updates_list),
    )
    aioresponse.get(
        "https://www.mangaupdates.com/series/ijystpf/akatsuki-no-aria",
        body=str(manga_updates_title),
    )
    aioresponse.get(
        "https://cdn.mangaupdates.com/image/i128641.png",
        body=bytes("img", "utf-8"),
    )
    async with manga_updates_container(title="Dawn Aria") as session:
        res = await session.get_image()
        assert res is None
