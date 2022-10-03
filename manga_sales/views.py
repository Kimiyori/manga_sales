
import aiohttp_jinja2
from aiohttp import web
from manga_sales.models import Week, Item
from sqlalchemy.engine.row import Row


@aiohttp_jinja2.template('index.html')
async def index(request: web.Request) -> dict[str, list[Week]]:
    async with request.app['db'].get_session() as session:
        data = await Week.get_all_groupby(session)
        return {'dates': data}


@aiohttp_jinja2.template('detail.html')
async def detail(request: web.Request) -> dict[str, list[Item]]:
    date = request.match_info['date']
    async with request.app['db'].get_session() as session:
        data = await Item.get_instance(session, date)
        return {'data': data}
