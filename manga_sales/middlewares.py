import aiohttp_jinja2
from aiohttp import web
from aiohttp_security import forget, authorized_userid
from aiohttp_session import get_session


async def handle_404(request:web.Request):
    return aiohttp_jinja2.render_template('404.html', request, {}, status=404)


async def handle_500(request:web.Request):
    return aiohttp_jinja2.render_template('500.html', request, {}, status=500)


def create_error_middleware(overrides):

    @web.middleware
    async def error_middleware(request:web.Request, handler):
        try:
            return await handler(request)
        except web.HTTPException as ex:
            override = overrides.get(ex.status)
            if override:
                return await override(request)

            raise
        except Exception:
            request.protocol.logger.exception("Error handling request")
            return await overrides[500](request)

    return error_middleware




@web.middleware
async def session_middleware(request, handler):
    request.session = await get_session(request)
    return await handler(request)


def setup_middlewares(app):
    error_middleware = create_error_middleware({
        404: handle_404,
        500: handle_500
    })
    app.middlewares.append(error_middleware)
    #app.middlewares.append(session_middleware)
