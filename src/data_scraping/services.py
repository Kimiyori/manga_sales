from pathlib import Path
from typing import Any


def save_image(
    source: str, source_type: str, file: bytes, name: str, date: str
) -> None:
    """Saves image in path defined with source and data_type arguments with following path:
        Path: 'manga_sales/static/images/{source}/{data_type}/'

    Args:
        source (str): type of source data (oricon etc)
        data_type (str): data type (weekly, monthly etc)
        file (bytes): image file that need to be saved
        name (str): file name
        date (str): date in string format
    """
    # confirm that all arguments needed for path are str type
    assert (
        isinstance(source, str)
        and isinstance(source_type, str)
        and isinstance(date, str)
    )
    image_path = (
        f"src/manga_sales/static/images/{source.lower()}/{source_type.lower()}/{date}"
    )
    if file and name:
        path = Path(image_path)
        # ensure that given path exist or create it
        path.mkdir(parents=True, exist_ok=True)
        with open(path / f"{name}", "wb") as open_file:
            open_file.write(file)


async def session_factory(scraper: Any, *args: Any, **kwargs: Any) -> Any:
    async with scraper(*args, **kwargs) as obj:
        yield obj


# async def get_date(
#     self,
#     session: AsyncSession,
#     date: datetime.date | None = None,
# ) -> datetime.date | None:
#     if not date:
#         check_date = await Week.get_last_date(
#             session, self.scraper.SOURCE, self.scraper.SOURCE_TYPE
#         )
#         date = check_date if check_date else datetime.date.today()
#     valid_date: datetime.date | None = await self.scraper.find_latest_date(date)
#     if valid_date:
#         check = await Week.get(session, valid_date)
#         if check:
#             return await self.get_date(session, valid_date)
#     return valid_date


# async def execute_scraper():
#     d=DataScrapingContaiter()
#     w=await d.oricon_scraper()
#     a = DatabaseConnector(w)
#     print(a.session)
