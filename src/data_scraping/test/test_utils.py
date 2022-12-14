from src.data_scraping.utils.url import build_url, update_url


def test_build_url():
    url = build_url(
        scheme="https",
        netloc="www.cdjapan.co.jp",
        path=["searchuni"],
        query={"term.media_format": "BOOK"},
    )
    assert "https://www.cdjapan.co.jp/searchuni?term.media_format=BOOK" == url
    url2 = build_url(
        scheme="https",
        netloc="www.mangaupdates.com",
        path=["series.html"],
        query={"filter": "no_oneshots", "type": "manga", "perpage": 10},
    )

    assert (
        "https://www.mangaupdates.com/series.html?filter=no_oneshots&type=manga&perpage=10"
        == url2
    )


def test_update_url():
    url = "https://www.cdjapan.co.jp/searchuni?term.media_format=BOOK"
    new_url = update_url(url, query={"search": "something", "q": "some"})
    assert new_url == url + "&search=something&q=some"
