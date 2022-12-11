from __future__ import annotations
import asyncio
import logging
import pathlib
import aiohttp_jinja2
import jinja2
from aiohttp_session import setup as setup_session
from aiohttp_session.redis_storage import RedisStorage
import redis
from aiohttp import web
from src.middlewares import setup_middlewares
from src.manga_sales.routes import setup_routes
from src.schedule import run_schedule
from src.template_functions import convert_date, file_exist


async def setup_redis(app_obj: web.Application) -> redis.asyncio.client.Redis[bytes]:
    pool: redis.asyncio.client.Redis[bytes] = await redis.asyncio.from_url(
        "redis://redis:6379"
    )

    async def close_redis(
        app_obj: web.Application,  # pylint: disable=unused-argument
    ) -> None:
        await pool.close()

    app_obj.on_cleanup.append(close_redis)
    app_obj["redis_pool"] = pool
    return pool


async def on_startup(
    app: web.Application,
):  # type:ignore # pylint: disable=unused-argument
    task = asyncio.create_task(run_schedule())
    await task

from pythonjsonlogger import jsonlogger
from datetime import datetime
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            # this doesn't use record.created, so it is slightly off
            log_record['timestamp'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname

async def create_app() -> web.Application:
    logging.basicConfig(level=logging.DEBUG)
    # formatter=logging.Formatter('%(message)s')
    # file_logger = logging.getLogger('file_log')
    # file_handler = logging.FileHandler('logs.log','w',
    #                           encoding = 'utf-8')
    # file_handler.setLevel(logging.DEBUG)
    # file_handler.setFormatter(formatter)
    # file_logger.addHandler(file_handler)
    # file_logger = logging.getLogger('file_log2')
    # file_handler = logging.FileHandler('logs2.log','w',
    #                           encoding = 'utf-8')
    # file_handler.setLevel(logging.DEBUG)
    # file_handler.setFormatter(formatter)
    # file_logger.addHandler(file_handler)
    app = web.Application()
    setup_routes(app)
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.FileSystemLoader(
            str(pathlib.Path(__file__).parent.parent / "src" / "templates")
        ),
    )
    env = aiohttp_jinja2.get_env(app)
    env.globals.update(convert_date=convert_date, file_exist=file_exist)
    redis_pool = await setup_redis(app)
    storage = RedisStorage(redis_pool)
    setup_session(app, storage)
    #app.on_startup.append(on_startup)
    return app


async def main() -> web.Application:
    app = await create_app()
    setup_middlewares(app)
    return app
