import aiohttp_jinja2
from sqlalchemy.engine.row import Row
from aiohttp import web
from manga_sales.models import Source, SourceType, Week, Item


@aiohttp_jinja2.template("source.html")
async def source(request: web.Request) -> dict[str, list[Row]]:
    """View for page with sources

    Args:
        request (web.Request)

    Returns:
        dict[str, list[Row]]: json with all sources
    """
    async with request.app["db"].get_session() as session:
        data = await Source.get_all(session)
        return {"data": data}


@aiohttp_jinja2.template("source_type.html")
async def source_type(request: web.Request) -> dict[str, list[SourceType | None]]:
    """View for page with source types

    Args:
        request (web.Request)

    Returns:
        dict[str, list[Row]]: json with all source types from given source
    """
    source_name = request.match_info["source"]
    async with request.app["db"].get_session() as session:
        data = await SourceType.get(session, source_name)
        return {"data": data}


@aiohttp_jinja2.template("source_type_detail.html")
async def source_type_detail(request: web.Request) -> dict[str, list[Week]]:
    """View for page with weeks from given source type and source

    Args:
        request (web.Request)

    Returns:
        dict[str, list[Row]]: json with weeks
    """
    source_str = request.match_info["source"]
    source_type_str = request.match_info["type"]
    async with request.app["db"].get_session() as session:
        data = await Week.get_all_groupby(session, source_str, source_type_str)
        return {"dates": data}


@aiohttp_jinja2.template("detail.html")
async def detail(request: web.Request) -> dict[str, list[Row]]:
    """View for page with items from given week

    Args:
        request (web.Request)

    Returns:
        dict[str, list[Row]]: items
    """
    date = request.match_info["date"]
    async with request.app["db"].get_session() as session:
        data = await Item.get_instance(session, date)
        return {"data": data}
