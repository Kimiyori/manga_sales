from dataclasses import dataclass
from datetime import date
from aiohttp import ClientResponse


@dataclass
class Content:
    """
    Common base class for representation title
    """

    name: str
    volume: int | None
    image: str | None
    imageb: ClientResponse | None
    authors: list[str]
    publisher: list[str]
    release_date: date | None
    rating: int
    sold: int
