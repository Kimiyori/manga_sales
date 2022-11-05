import datetime
import functools
from typing import Any, Awaitable, Callable, Coroutine, ParamSpec, TypeVar
from dependency_injector.wiring import Provide, inject, Closing
from src.data_scraping.containers import DBSessionContainer, DataScrapingContainer
from src.data_scraping.database_saver import DatabaseConnector
from src.data_scraping.main_scrapers.abc import MainDataAbstractScraper
from src.manga_sales.db.data_access_layers.week import WeekDAO

MainFuncParams = ParamSpec("MainFuncParams")
MainFunc = TypeVar("MainFunc")


def return_db_cont() -> DBSessionContainer:
    return DBSessionContainer()


def create_db_container(
    func: Callable[MainFuncParams, Awaitable[MainFunc]]
) -> Callable[MainFuncParams, Coroutine[Any, Any, None]]:
    @functools.wraps(func)
    async def wrapper(
        *args: MainFuncParams.args, **kwargs: MainFuncParams.kwargs
    ) -> None:
        db_cont = return_db_cont()
        await func(*args, **kwargs)
        db_cont.unwire()  # pylint: disable=no-member

    return wrapper


def create_scraper_container(
    func: Callable[MainFuncParams, Awaitable[MainFunc]]
) -> Callable[MainFuncParams, Coroutine[Any, Any, None]]:
    @functools.wraps(func)
    async def wrapper(
        *args: MainFuncParams.args, **kwargs: MainFuncParams.kwargs
    ) -> None:
        scrap_cont = DataScrapingContainer()
        await func(*args, **kwargs)
        await scrap_cont.shutdown_resources()  # type: ignore  # pylint: disable=no-member

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
    week_session: WeekDAO = Closing[Provide[DBSessionContainer.week]],
) -> datetime.date | None:
    if date is None:
        check_date = await week_session.get_last_date(
            scraper.SOURCE, scraper.SOURCE_TYPE
        )
        date = check_date if check_date else datetime.date.today()
    valid_date = await scraper.find_latest_date(date)
    assert valid_date is None or isinstance(valid_date, datetime.date)
    if valid_date:
        check = await week_session.get(valid_date)
        if check:
            return await get_date(scraper, valid_date)
    return valid_date


@create_db_container
@create_scraper_container
async def execute_scraper(scraper_name: str, date: datetime.date | None = None) -> None:
    scraper = await scraper_factory(scraper_name)
    if date is None:
        date = await get_date(scraper)
    if date:
        db_conn = DatabaseConnector(scraper)
        await db_conn.insert_data(date)
        date_new = await get_date(scraper, date)
        if date_new:
            await execute_scraper(scraper_name, date_new)