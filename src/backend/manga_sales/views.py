import json
import aiohttp_jinja2
from sqlalchemy.engine.row import Row
from dependency_injector.wiring import Provide, inject, Closing
from aiohttp import web
from manga_sales.containers import DatabaseContainer
from manga_sales.db.data_access_layers.item import ItemDAO
from manga_sales.db.data_access_layers.source import SourceDAO
from manga_sales.db.data_access_layers.source_type import SourceTypeDAO
from manga_sales.db.data_access_layers.week import WeekDAO
from manga_sales.db.models import SourceType, Week


# @aiohttp_jinja2.template("source.html")
@inject
async def source(
    request: web.Request,  # pylint: disable = unused-argument
    service: SourceDAO = Closing[Provide[DatabaseContainer.source]],
) -> web.Response:
    """View for page with sources

    Args:
        request (web.Request)

    Returns:
        dict[str, list[Row]]: json with all sources
    """
    data = await service.get_all()
    print(data)
    response = [{"name": source[0], "image": source[1]} for source in data]
    return web.Response(text=json.dumps(response), content_type="application/json")


# @aiohttp_jinja2.template("source_type.html")
@inject
async def source_type(
    request: web.Request,
    service: SourceTypeDAO = Closing[Provide[DatabaseContainer.source_type]],
) -> web.Response:
    """View for page with source types

    Args:
        request (web.Request)

    Returns:
        dict[str, list[Row]]: json with all source types from given source
    """
    source_name = request.match_info["source"]
    data = await service.get(source_name)
    response = [{"type": item.type} for item in data]
    return web.Response(text=json.dumps(response), content_type="application/json")


#@aiohttp_jinja2.template("source_type_detail.html")
@inject
async def source_type_detail(
    request: web.Request,
    service: WeekDAO = Closing[Provide[DatabaseContainer.week]],
) -> dict[str, list[Week]]:
    """View for page with weeks from given source type and source

    Args:
        request (web.Request)

    Returns:
        dict[str, list[Row]]: json with weeks
    """
    source_str = request.match_info["source"]
    source_type_str = request.match_info["type"]
    data = await service.get_all_groupby(source_str, source_type_str)
    return web.Response(text=json.dumps(data), content_type="application/json")


@aiohttp_jinja2.template("detail.html")
@inject
async def detail(
    request: web.Request,
    service: ItemDAO = Closing[Provide[DatabaseContainer.item]],
) -> dict[str, list[Row]]:
    """View for page with items from given week

    Args:
        request (web.Request)

    Returns:
        dict[str, list[Row]]: items
    """
    date = request.match_info["date"]
    data = await service.get_instance(date)
    return {"data": data}
