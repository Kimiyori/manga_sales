from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
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
    publishers: list[str]
    rating: int
    release_date: date | None = field(default=None)
    sales: int | None = field(default=None)
