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
from template_functions import convert_date, file_exist
from middlewares import setup_middlewares
from manga_sales.routes import setup_routes
from schedule import run_schedule


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
    app: web.Application,  # pylint: disable=unused-argument
) -> None:
    task = asyncio.create_task(run_schedule())
    await task


async def create_app() -> web.Application:
    logging.basicConfig(level=logging.DEBUG)
    app = web.Application()
    setup_routes(app)
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.FileSystemLoader(
            str(pathlib.Path(__file__).parent.parent / "backend" / "templates")
        ),
    )
    env = aiohttp_jinja2.get_env(app)
    env.globals.update(convert_date=convert_date, file_exist=file_exist)
    redis_pool = await setup_redis(app)
    storage = RedisStorage(redis_pool)
    setup_session(app, storage)
    # app.on_startup.append(on_startup)
    return app


async def main() -> web.Application:
    app = await create_app()
    setup_middlewares(app)
    return app
