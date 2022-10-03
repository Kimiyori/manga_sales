
import pathlib
from manga_sales.views import detail, index
from aiohttp.web import Application
PROJECT_ROOT = pathlib.Path(__file__).parent


def setup_routes(app: Application) -> None:
    app.router.add_get('/', index, name='index')
    app.router.add_get(
        r'/oricon/{date:[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])}/', detail, name='detail')
