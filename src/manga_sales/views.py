import aiohttp_jinja2
from sqlalchemy.engine.row import Row
from aiohttp import web
from dependency_injector.wiring import Provide, inject
from src.manga_sales.containers import DatabaseContainer
from src.manga_sales.db.data_access_layers.abc import DAOType
from src.manga_sales.db.models import SourceType, Week


@aiohttp_jinja2.template("source.html")
@inject
async def source(
    request: web.Request,  # pylint: disable = unused-argument
    service: DAOType = Provide[DatabaseContainer.source_session],
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
    service: DAOType = Provide[DatabaseContainer.sourcetype_session],
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
    request: web.Request, service: DAOType = Provide[DatabaseContainer.week_session]
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
    request: web.Request, service: DAOType = Provide[DatabaseContainer.item_session]
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
