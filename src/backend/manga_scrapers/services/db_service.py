import datetime
import functools
from typing import Any, Awaitable, Callable, Coroutine, ParamSpec, TypeVar
from dependency_injector.wiring import Provide, inject, Closing
from manga_scrapers.containers.title_data_container import AuxScrapingContainer
from manga_scrapers.containers.image_container import ImageScrapingContainer
from manga_scrapers.containers.rating_container import DataScrapingContainer
from manga_scrapers.database_handler import DatabaseConnector
from manga_scrapers.scrapers.rating_scrapers.meta import MainDataAbstractScraper
from manga_sales.db.data_access_layers.week import WeekDAO
from manga_sales.containers import DatabaseContainer

MainFuncParams = ParamSpec("MainFuncParams")
MainFunc = TypeVar("MainFunc")


def return_db_cont() -> DatabaseContainer:
    """Function to invode container for database"""
    return DatabaseContainer()


def create_db_container(
    func: Callable[MainFuncParams, Awaitable[MainFunc]]
) -> Callable[MainFuncParams, Coroutine[Any, Any, None]]:
    @functools.wraps(func)
    async def wrapper(
        *args: MainFuncParams.args, **kwargs: MainFuncParams.kwargs
    ) -> None:
        db_cont = return_db_cont()
        try:
            await func(*args, **kwargs)
        finally:
            db_cont.unwire()  # pylint: disable=no-member

    return wrapper


def create_scraper_container(
    func: Callable[MainFuncParams, Awaitable[MainFunc]]
) -> Callable[MainFuncParams, Coroutine[Any, Any, None]]:
    @functools.wraps(func)
    async def wrapper(
        *args: MainFuncParams.args, **kwargs: MainFuncParams.kwargs
    ) -> None:
        main_scrap = DataScrapingContainer()
        aux_scrap = AuxScrapingContainer()
        image_scrap = ImageScrapingContainer()
        try:
            await func(*args, **kwargs)
        finally:
            await main_scrap.shutdown_resources()  # type: ignore  # pylint: disable=no-member
            await aux_scrap.shutdown_resources()  # type: ignore  # pylint: disable=no-member
            await image_scrap.shutdown_resources()  # type: ignore  # pylint: disable=no-member

    return wrapper


@inject
async def scraper_factory(
    scraper_name: str,
    container: DataScrapingContainer = Closing[Provide[DataScrapingContainer]],
) -> MainDataAbstractScraper:
    try:
        scraper_obj: Callable[..., MainDataAbstractScraper] = getattr(
            container, scraper_name
        )
        return await scraper_obj()  # type: ignore
    except AttributeError as exc:
        raise exc


@inject
async def get_date(
    scraper: MainDataAbstractScraper,
    date: datetime.date | None = None,
    week_session: WeekDAO = Closing[Provide[DatabaseContainer.week]],
) -> datetime.date | None:
    action = "backward"
    if date is None:
        last_db_date = await week_session.get_last_date(
            scraper.SOURCE, scraper.SOURCE_TYPE
        )
        if last_db_date:
            date, action = last_db_date, "forward"
        else:
            date = datetime.date.today()
    valid_date = await scraper.find_latest_date(date, action)

    assert valid_date is None or isinstance(valid_date, datetime.date)
    if valid_date:
        if await week_session.get(valid_date):
            return await get_date(scraper, valid_date)
    return valid_date


@create_db_container
@create_scraper_container
async def execute_scraper(scraper_name: str, date: datetime.date | None = None) -> None:
    scraper = await scraper_factory(scraper_name)
    db_conn = DatabaseConnector(scraper)
    if date is None:
        date = await get_date(scraper)
    while date:
        await db_conn.insert_data(date)
        date = await get_date(scraper, date)
