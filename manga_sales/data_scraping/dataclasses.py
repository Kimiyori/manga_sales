from dataclasses import dataclass
from datetime import date
from aiohttp import web

@dataclass
class Content:
    """
    Common base class for representation title
    """
    name: str
    volume: int|None
    image:str
    imageb:web.Response
    authors: list[str]
    publisher: list[str]
    release_date: date
    rating: int
    sold: int
