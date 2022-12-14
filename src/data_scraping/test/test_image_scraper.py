from unittest import mock
import pytest

from src.data_scraping.utils.url import build_url
from .conftest import cdjapan_item, cdjapan_list, cdjapan_container, aioresponse


@pytest.mark.asyncio
async def test_get_image_cdjapan(
    aioresponse, cdjapan_container, cdjapan_item, cdjapan_list
):
    search_name = "怪獣8号 8"
    filter_name = "Kaiju No. 8"
    volume = 8

    aioresponse.get(
        build_url(
            scheme="https",
            netloc="www.cdjapan.co.jp",
            path=["searchuni"],
            query={"term.media_format": "BOOK", "q": f"{search_name} {volume}"},
        ),
        status=200,
        body=str(cdjapan_list),
    )
    aioresponse.get(
        "https://www.cdjapan.co.jp/product/NEOBK-2788024",
        status=200,
        body=str(cdjapan_item),
    )
    aioresponse.get(
        "https://st.cdjapan.co.jp/pictures/l/02/24/NEOBK-2788024.jpg?v=1",
        status=200,
        body=bytes("img", "utf-8"),
    )
    image = await cdjapan_container.get_image(search_name, filter_name, volume)
    assert isinstance(image, bytes)
