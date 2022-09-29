
import aiohttp_jinja2
from aiohttp import web
from manga_sales.models import Week, Item


@aiohttp_jinja2.template('index.html')
async def index(request: web.Request):
    async with request.app['db'].get_session as session:
        data = await Week.get_all_groupby(session)
        return {'dates': data}


@aiohttp_jinja2.template('detail.html')
async def detail(request: web.Request):
    date = request.match_info['date']
    async with request.app['db'].get_session as session:
        data = await Item.get_instance(session, date)
        return {'data': data}
