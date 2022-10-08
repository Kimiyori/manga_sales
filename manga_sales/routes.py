import pathlib
from manga_sales.views import detail, source_type_detail, source, source_type
from aiohttp.web import Application

PROJECT_ROOT = pathlib.Path(__file__).parent


def setup_routes(app: Application) -> None:
    app.router.add_get("/", source, name="source")
    app.router.add_get(r"/{source:\w+}/", source_type, name="source_type")
    app.router.add_get(
        r"/{source:\w+}/{type:\w+}/", source_type_detail, name="source_type_detail"
    )
    app.router.add_get(
        r"/{source:\w+}/{type:\w+}/{date:[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])}/",
        detail,
        name="detail",
    )
