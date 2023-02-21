from __future__ import annotations
import asyncio
import logging
from aiohttp_session import setup as setup_session
from aiohttp_session.redis_storage import RedisStorage
import redis
from aiohttp import web
from config.middlewares import setup_middlewares
from manga_sales.routes import setup_routes
from config.schedule import run_schedule


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
    asyncio.create_task(run_schedule())


async def create_app() -> web.Application:
    logging.basicConfig(level=logging.DEBUG)
    app = web.Application()
    setup_routes(app)
    redis_pool = await setup_redis(app)
    storage = RedisStorage(redis_pool)
    setup_session(app, storage)
    app.on_startup.append(on_startup)
    return app


async def main() -> web.Application:
    app = await create_app()
    setup_middlewares(app)
    return app
