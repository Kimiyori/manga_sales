import aiohttp_jinja2
from aiohttp_session import get_session
from aiohttp import web
from aiohttp.typedefs import Handler
from aiohttp.web_middlewares import _Middleware


async def handle_404(request: web.Request) -> web.Response:
    return aiohttp_jinja2.render_template("404.html", request, {}, status=404)


async def handle_500(request: web.Request) -> web.Response:
    return aiohttp_jinja2.render_template("500.html", request, {}, status=500)


def create_error_middleware(overrides: dict[int, Handler]) -> _Middleware:
    @web.middleware
    async def error_middleware(
        request: web.Request, handler: Handler
    ) -> web.StreamResponse:
        try:
            return await handler(request)
        except web.HTTPException as ex:
            override = overrides.get(ex.status)
            if override:
                return await override(request)

            raise
    return error_middleware


@web.middleware
async def session_middleware(
    request: web.Request, handler: Handler
) -> web.StreamResponse:
    request.session = await get_session(request)
    return await handler(request)


def setup_middlewares(app: web.Application) -> None:
    error_middleware = create_error_middleware({404: handle_404, 500: handle_500})
    app.middlewares.append(error_middleware)
    # app.middlewares.append(session_middleware)
