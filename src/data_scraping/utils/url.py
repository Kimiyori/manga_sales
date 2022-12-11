from urllib.parse import urlencode, urlunparse, urlparse
from functools import wraps
import inspect

PREFIX = {"path": "/", "query": "&"}


def deco(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs.get("path"):
            kwargs["path"] = "/".join(kwargs["path"])
        if kwargs.get("query"):
            kwargs["query"] = urlencode(kwargs["query"])
        return func(*args, **kwargs)

    return wrapper


@deco
def build_url(scheme, netloc, path="", parameters="", query="", anchor="", trailing_slash=False):
    url_parts = [""] * 6
    frame = inspect.currentframe()
    keys, _, _, _ = inspect.getargvalues(frame)
    for index, part in enumerate(keys[:-1]):
        url_parts[index] = locals()[part]
    return urlunparse(url_parts) + "/" if trailing_slash else urlunparse(url_parts)


@deco
def update_url(url, path="", parameters="", query="", anchor="", trailing_slash=False):
    url_parts = list(urlparse(url))
    frame = inspect.currentframe()
    keys, _, _, _ = inspect.getargvalues(frame)
    for index, part in enumerate(keys[1:-1], start=2):
        if locals()[part]:
            url_parts[index] += PREFIX[part] + locals()[part]
    return urlunparse(url_parts) + "/" if trailing_slash else urlunparse(url_parts)
