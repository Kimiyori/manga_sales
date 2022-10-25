import logging
import pathlib
import aiohttp_jinja2
import jinja2
from aiohttp_session import setup as setup_session
from aiohttp_session.redis_storage import RedisStorage
import aioredis
from aioredis.client import Redis
from aiohttp import web
from src.middlewares import setup_middlewares
from src.manga_sales.routes import setup_routes
from src.template_functions import convert_date, file_exist
from src.manga_sales.containers import DatabaseContainer


async def setup_redis(app_obj: web.Application) -> Redis:
    pool: Redis = await aioredis.from_url("redis://redis:6379")

    async def close_redis(
        app_obj: web.Application,  # pylint: disable=unused-argument
    ) -> None:
        await pool.close()

    app_obj.on_cleanup.append(close_redis)
    app_obj["redis_pool"] = pool
    return pool


async def main() -> web.Application:
    logging.basicConfig(level=logging.DEBUG)
    app = web.Application()
    setup_routes(app)
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.FileSystemLoader(
            str(pathlib.Path(__file__).parent.parent / "src" / "templates")
        ),
    )
    setup_middlewares(app)
    env = aiohttp_jinja2.get_env(app)
    env.globals.update(convert_date=convert_date, file_exist=file_exist)
    redis_pool = await setup_redis(app)
    setup_session(app, RedisStorage(redis_pool))
    DatabaseContainer()
    return app
