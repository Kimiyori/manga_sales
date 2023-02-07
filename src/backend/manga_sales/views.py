import json
import aiohttp_jinja2
from dependency_injector.wiring import Provide, inject, Closing
from aiohttp import web

from manga_sales.containers import DatabaseContainer
from manga_sales.db.data_access_layers.item import ItemDAO
from manga_sales.db.data_access_layers.source import SourceDAO
from manga_sales.db.data_access_layers.source_type import SourceTypeDAO
from manga_sales.db.data_access_layers.week import WeekDAO


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
    response = [
        {
            "name": source[1],
            "image": source[2],
            "description": source[3],
            "link": source[4],
            "types": source[5],
        }
        for source in data
    ]
    return web.Response(text=json.dumps(response), content_type="application/json")


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
    response = [{"type": item.type} for item in data] if data else None
    return web.Response(text=json.dumps(response), content_type="application/json")


@inject
async def source_type_detail(
    request: web.Request,
    service: WeekDAO = Closing[Provide[DatabaseContainer.week]],
) -> web.Response:
    """View for page with weeks from given source type and source

    Args:
        request (web.Request)

    Returns:
        dict[str, list[Row]]: json with weeks
    """
    source_str = request.match_info["source"]
    source_type_str = request.match_info["type"]
    data = await service.get_all_groupby(source_str, source_type_str)
    formatted_data = [
        {
            "year": year,
            "months": [
                {"name": name, "dates": dates} for (name, dates) in months.items()
            ],
        }
        for item in data
        for (year, months) in item.items()
    ]
    return web.Response(
        text=json.dumps(formatted_data), content_type="application/json"
    )


@aiohttp_jinja2.template("detail.html")
@inject
async def detail(
    request: web.Request,
    service: ItemDAO = Closing[Provide[DatabaseContainer.item]],
) -> web.Response:
    """View for page with items from given week

    Args:
        request (web.Request)

    Returns:
        dict[str, list[Row]]: items
    """
    date = request.match_info["date"]
    data = await service.get_instance(date)
    formatted_data = [
        {
            "title": item.title,
            "rating": item.rating,
            "volume": item.volume,
            "release_date": item.release_date.strftime("%d-%m-%Y")
            if item.release_date
            else None,
            "authors": item.authors,
            "publishers": item.publishers,
            "image": item.image,
            "sales": item.sold,
            "prev_rank": item.previous_rank.name if item.previous_rank else None,
        }
        for item in data
    ]
    return web.Response(
        text=json.dumps(formatted_data), content_type="application/json"
    )
