import aiohttp_jinja2
from sqlalchemy.engine.row import Row
from dependency_injector.wiring import Provide, inject, Closing
from aiohttp import web
from src.manga_sales.containers import DatabaseContainer
from src.manga_sales.db.data_access_layers.item import ItemDAO
from src.manga_sales.db.data_access_layers.source import SourceDAO
from src.manga_sales.db.data_access_layers.source_type import SourceTypeDAO
from src.manga_sales.db.data_access_layers.week import WeekDAO
from src.manga_sales.db.models import SourceType, Week


@aiohttp_jinja2.template("source.html")
@inject
async def source(
    request: web.Request,  # pylint: disable = unused-argument
    service: SourceDAO = Closing[Provide[DatabaseContainer.source_session]],  # type: ignore
) -> dict[str, list[Row]]:
    """View for page with sources

    Args:
        request (web.Request)

    Returns:
        dict[str, list[Row]]: json with all sources
    """
    data = await service.get_all()
    return {"data": data}


@aiohttp_jinja2.template("source_type.html")
@inject
async def source_type(
    request: web.Request,
    service: SourceTypeDAO = Closing[Provide[DatabaseContainer.sourcetype_session]],  # type: ignore
) -> dict[str, list[SourceType | None]]:
    """View for page with source types

    Args:
        request (web.Request)

    Returns:
        dict[str, list[Row]]: json with all source types from given source
    """
    source_name = request.match_info["source"]
    data = await service.get(source_name)
    return {"data": data}


@aiohttp_jinja2.template("source_type_detail.html")
@inject
async def source_type_detail(
    request: web.Request,
    service: WeekDAO = Closing[Provide[DatabaseContainer.week_session]],  # type: ignore
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
    return {"dates": data}


@aiohttp_jinja2.template("detail.html")
@inject
async def detail(
    request: web.Request,
    service: ItemDAO = Closing[Provide[DatabaseContainer.item_session]],  # type: ignore
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
