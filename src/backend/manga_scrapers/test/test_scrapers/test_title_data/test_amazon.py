from datetime import date
import datetime
import pytest

from manga_scrapers.utils.url_handler import build_url
from manga_scrapers.test.conftest import (
    amazon_container,
    amazon_list,
    aioresponse,
    amazon_item,
    proxy_mock
)


@pytest.mark.asyncio
async def test_get_main_info_page(aioresponse, amazon_list, amazon_container):
    url = build_url(
        scheme="https",
        netloc="www.amazon.co.jp",
        path=["s"],
        query={"k": 9784041126202, "i": "stripbooks", "s": "date-desc-rank"},
    )
    aioresponse.get(url, body=str(amazon_list))
    aioresponse.get(
        "https://www.amazon.co.jp/-/en/%E7%B7%92%E6%96%B9%E4%BF%8A%E8%BC%94-ebook/dp/B0BBZTP6XT/ref=sr_1_1?camp=247&creative=1211&keywords=9784041126202&linkCode=ur2&linkId=9f125b3efa3f20f629497ff6e3168289&qid=1671299756&s=books&sr=1-1",
        body="test",
    )
    async with amazon_container(
        title="賢者の孫", volume=None, isbn=9784041126202, publication_date=date(2022, 9, 9)
    ) as scraper:
        assert scraper.volume == 20
        assert str(scraper.page) == "test"

def test_get_most_similar_title_without_volume(amazon_list, amazon_container):
    obj = amazon_container(
        title="賢者の孫", volume=None, isbn=9784041126202, publication_date=date(2022, 9, 9)
    )
    title = obj._get_most_similar_title(amazon_list)
    assert title == {
        "volume": 20,
        "link": "https://www.amazon.co.jp/-/en/%E7%B7%92%E6%96%B9%E4%BF%8A%E8%BC%94-ebook/dp/B0BBZTP6XT/ref=sr_1_1?camp=247&creative=1211&keywords=9784041126202&linkCode=ur2&linkId=9f125b3efa3f20f629497ff6e3168289&qid=1671299756&s=books&sr=1-1",
        "publication_date": datetime.date(2022, 9, 9),
    }

def test_get_most_similar_title_with_volume(amazon_list, amazon_container):
    obj = amazon_container(
        title="賢者の孫", volume=14, isbn=9784041126202, publication_date=date(2020, 8, 9)
    )
    title = obj._get_most_similar_title(amazon_list)
    assert title == {
        "volume": 14,
        "link": "https://www.amazon.co.jp/-/en/%E7%B7%92%E6%96%B9%E4%BF%8A%E8%BC%94-ebook/dp/B08BWZ5N9N/ref=sr_1_3?camp=247&creative=1211&keywords=9784041126202&linkCode=ur2&linkId=9f125b3efa3f20f629497ff6e3168289&qid=1671299756&s=books&sr=1-3",
        "publication_date": datetime.date(2020, 8, 10),
    }

def test_get_most_similar_title_mismatch_date_and_volume(amazon_list, amazon_container):
    obj = amazon_container(
        title="賢者の孫", volume=20, isbn=9784041126202, publication_date=date(2020, 8, 9)
    )
    title = obj._get_most_similar_title(amazon_list)
    assert title == None

@pytest.mark.asyncio
async def test_get_volume(aioresponse, amazon_list, amazon_container):
    url = build_url(
        scheme="https",
        netloc="www.amazon.co.jp",
        path=["s"],
        query={"k": 9784041126202, "i": "stripbooks", "s": "date-desc-rank"},
    )
    aioresponse.get(url, body=str(amazon_list))
    aioresponse.get(
        "https://www.amazon.co.jp/-/en/%E7%B7%92%E6%96%B9%E4%BF%8A%E8%BC%94-ebook/dp/B0BBZTP6XT/ref=sr_1_1?camp=247&creative=1211&keywords=9784041126202&linkCode=ur2&linkId=9f125b3efa3f20f629497ff6e3168289&qid=1671299756&s=books&sr=1-1",
        body="test",
    )
    async with amazon_container(
        title="賢者の孫", volume=None, isbn=9784041126202, publication_date=date(2022, 9, 9)
    ) as scraper:
        assert scraper.get_volume() == 20

@pytest.mark.asyncio
async def test_get_authors(aioresponse, amazon_list, amazon_item, amazon_container):
    url = build_url(
        scheme="https",
        netloc="www.amazon.co.jp",
        path=["s"],
        query={"k": 9784041126202, "i": "stripbooks", "s": "date-desc-rank"},
    )
    aioresponse.get(url, body=str(amazon_list))
    aioresponse.get(
        "https://www.amazon.co.jp/-/en/%E7%B7%92%E6%96%B9%E4%BF%8A%E8%BC%94-ebook/dp/B0BBZTP6XT/ref=sr_1_1?camp=247&creative=1211&keywords=9784041126202&linkCode=ur2&linkId=9f125b3efa3f20f629497ff6e3168289&qid=1671299756&s=books&sr=1-1",
        body=str(amazon_item),
    )
    async with amazon_container(
        title="賢者の孫", volume=None, isbn=9784041126202, publication_date=date(2022, 9, 9)
    ) as scraper:
        assert scraper.get_authors() == ["緒方俊輔"]

@pytest.mark.asyncio
async def test_get_publisers(aioresponse, amazon_list, amazon_item, amazon_container):
    url = build_url(
        scheme="https",
        netloc="www.amazon.co.jp",
        path=["s"],
        query={"k": 9784041126202, "i": "stripbooks", "s": "date-desc-rank"},
    )
    aioresponse.get(url, body=str(amazon_list))
    aioresponse.get(
        "https://www.amazon.co.jp/-/en/%E7%B7%92%E6%96%B9%E4%BF%8A%E8%BC%94-ebook/dp/B0BBZTP6XT/ref=sr_1_1?camp=247&creative=1211&keywords=9784041126202&linkCode=ur2&linkId=9f125b3efa3f20f629497ff6e3168289&qid=1671299756&s=books&sr=1-1",
        body=str(amazon_item),
    )
    async with amazon_container(
        title="賢者の孫", volume=None, isbn=9784041126202, publication_date=date(2022, 9, 9)
    ) as scraper:
        assert scraper.get_publishers() == ["KADOKAWA"]

@pytest.mark.asyncio
async def test_get_image(aioresponse, amazon_list, amazon_item, amazon_container):
    url = build_url(
        scheme="https",
        netloc="www.amazon.co.jp",
        path=["s"],
        query={"k": 9784041126202, "i": "stripbooks", "s": "date-desc-rank"},
    )
    aioresponse.get(url, body=str(amazon_list))
    aioresponse.get(
        "https://www.amazon.co.jp/-/en/%E7%B7%92%E6%96%B9%E4%BF%8A%E8%BC%94-ebook/dp/B0BBZTP6XT/ref=sr_1_1?camp=247&creative=1211&keywords=9784041126202&linkCode=ur2&linkId=9f125b3efa3f20f629497ff6e3168289&qid=1671299756&s=books&sr=1-1",
        body=str(amazon_item),
    )
    aioresponse.get("https://m.media-amazon.com/images/I/51o8psL5rwL.jpg", body=b"test")
    async with amazon_container(
        title="賢者の孫", volume=None, isbn=9784041126202, publication_date=date(2022, 9, 9)
    ) as scraper:
        img = await scraper.get_image()
        assert isinstance(img, bytes)
