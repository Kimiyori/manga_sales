from dataclasses import dataclass
from datetime import date


@dataclass
class Content:
    """
    Common base class for representation title
    """

    # pylint: disable=too-many-instance-attributes
    # Eight is reasonable in this case.
    name: str
    volume: int | None
    image: str | None
    authors: list[str]
    publisher: list[str]
    release_date: date | None
    rating: int
    sold: int | None
