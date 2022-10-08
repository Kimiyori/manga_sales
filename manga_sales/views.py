import aiohttp_jinja2
from aiohttp import web
from manga_sales.models import Source, SourceType, Week, Item
from sqlalchemy.engine.row import Row


@aiohttp_jinja2.template("source.html")
async def source(request: web.Request) -> dict[str, list[Row]]:
    async with request.app["db"].get_session() as session:
        data = await Source.get_all(session)
        return {"data": data}


@aiohttp_jinja2.template("source_type.html")
async def source_type(request: web.Request) -> dict[str, list[Row]]:
    source = request.match_info["source"]
    async with request.app["db"].get_session() as session:
        data = await SourceType.get(session, source)
        return {"data": data}


@aiohttp_jinja2.template("source_type_detail.html")
async def source_type_detail(request: web.Request) -> dict[str, list[Week]]:
    async with request.app["db"].get_session() as session:
        data = await Week.get_all_groupby(session)
        return {"dates": data}


@aiohttp_jinja2.template("detail.html")
async def detail(request: web.Request) -> dict[str, list[Row]]:
    date = request.match_info["date"]
    async with request.app["db"].get_session() as session:
        data = await Item.get_instance(session, date)
        return {"data": data}
