import datetime
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
from manga_sales.template_functions import convert_date, file_exist
from manga_sales.scheduler import PeriodicSchedule


async def setup_redis(app):

    pool = await aioredis.from_url("redis://redis:6379")

    async def close_redis(app):
        await pool.close()

    app.on_cleanup.append(close_redis)
    app['redis_pool'] = pool
    return pool


async def setup_tasks(app):
    schedule = PeriodicSchedule(app['db'])
    await schedule.start()

app = web.Application()
app['config'] = config
setup_routes(app)
session = AsyncDatabaseSession(app['config']['postgres'])
session.init()
app['db'] = session
aiohttp_jinja2.setup(app,
                     loader=jinja2.FileSystemLoader(
                         str(BASE_DIR / 'manga_sales' / 'templates')))
setup_middlewares(app)
env = aiohttp_jinja2.get_env(app)
env.globals.update(convert_date=convert_date, file_exist=file_exist)


async def main():
    # logging.basicConfig(level=logging.DEBUG)
    redis_pool = await setup_redis(app)
    setup_session(app, RedisStorage(redis_pool))
    # await setup_tasks(app)
    return app
