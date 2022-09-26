import logging
import sys

import aiohttp_jinja2
import jinja2
from aiohttp import web

from aiohttp_session import setup as setup_session
from aiohttp_session.redis_storage import RedisStorage
import aioredis
from manga_sales.db import AsyncDatabaseSession
from manga_sales.middlewares import setup_middlewares
from manga_sales.routes import setup_routes
from manga_sales.settings import config, BASE_DIR
import logging
import asyncio
from manga_sales.data_scraping.db_handle import DBWriter

async def setup_redis(app):

    pool = await aioredis.from_url("redis://redis:6379")

    async def close_redis(app):
        pool.close()
        await pool.wait_closed()

    app.on_cleanup.append(close_redis) 
    app['redis_pool'] = pool
    return pool



async def init_app():

    app = web.Application()

    app['config'] = config
    setup_routes(app)
    session=AsyncDatabaseSession(app['config']['postgres'])
    session.init()
    app['db']=session
    redis_pool = await setup_redis(app)
    setup_session(app, RedisStorage(redis_pool))
    # setup Jinja2 template renderer
    aiohttp_jinja2.setup(app,
                         loader=jinja2.FileSystemLoader(str(BASE_DIR / 'manga_sales' / 'templates')))


    #app.cleanup_ctx.append(pg_context)



    setup_middlewares(app)
    #asyncio.get_event_loop().create_task(DBWriter(app).write_data())
    return app




app = web.Application()
app['config'] = config
setup_routes(app)
session=AsyncDatabaseSession(app['config']['postgres'])
session.init()
app['db']=session
aiohttp_jinja2.setup(app,
                    loader=jinja2.FileSystemLoader(str(BASE_DIR / 'manga_sales' / 'templates')))


async def main():
    #logging.basicConfig(level=logging.DEBUG)
    redis_pool = await setup_redis(app)
    setup_session(app, RedisStorage(redis_pool))
    return app
