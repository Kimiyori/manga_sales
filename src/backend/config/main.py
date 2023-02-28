from __future__ import annotations
import asyncio
import logging
from aiohttp import web
from config.middlewares import setup_middlewares
from manga_sales.routes import setup_routes
from config.schedule import run_schedule


async def on_startup(
    app: web.Application,  # pylint: disable=unused-argument
) -> None:
    task = asyncio.create_task(run_schedule())
    await task


async def create_app() -> web.Application:
    logging.basicConfig(level=logging.DEBUG)
    app = web.Application()
    setup_routes(app)
    # app.on_startup.append(on_startup)
    return app


async def main() -> web.Application:
    app = await create_app()
    setup_middlewares(app)
    return app
