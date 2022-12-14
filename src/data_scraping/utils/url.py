# pylint: disable=unused-argument
from typing import Callable, ParamSpec
from urllib.parse import urlencode, urlunparse, urlparse
from functools import wraps
import inspect

MainFuncParams = ParamSpec("MainFuncParams")

PREFIX = {"path": "/", "query": "&"}


def deco(func: Callable[MainFuncParams, str]) -> Callable[MainFuncParams, str]:
    @wraps(func)
    def wrapper(*args: MainFuncParams.args, **kwargs: MainFuncParams.kwargs) -> str:
        if kwargs.get("path"):
            kwargs["path"] = "/".join(kwargs["path"])  # type: ignore
        if kwargs.get("query"):
            kwargs["query"] = urlencode(kwargs["query"])  # type: ignore
        return func(*args, **kwargs)

    return wrapper


@deco
def build_url(  # pylint: disable=dangerous-default-value, too-many-arguments
    scheme: str,
    netloc: str,
    path: list[str] = [],
    parameters: str = "",
    query: dict[str, str | int] = {},
    anchor: str = "",
    trailing_slash: bool = False,
) -> str:
    url_parts = [""] * 6
    frame = inspect.currentframe()
    keys, _, _, _ = inspect.getargvalues(frame)  # type: ignore
    for index, part in enumerate(keys[:-1]):
        url_parts[index] = locals()[part]
    return urlunparse(url_parts) + "/" if trailing_slash else urlunparse(url_parts)


@deco
def update_url(  # pylint: disable=dangerous-default-value, too-many-arguments
    url: str,
    path: list[str] = [],
    parameters: str = "",
    query: dict[str, str | int] = {},
    anchor: str = "",
    trailing_slash: bool = False,
) -> str:
    url_parts = list(urlparse(url))
    frame = inspect.currentframe()
    keys, _, _, _ = inspect.getargvalues(frame)  # type: ignore
    for index, part in enumerate(keys[1:-1], start=2):
        if locals()[part]:
            url_parts[index] += PREFIX[part] + locals()[part]
    return urlunparse(url_parts) + "/" if trailing_slash else urlunparse(url_parts)
