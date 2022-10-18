import asyncio
from contextlib import suppress
import datetime
from typing import Callable
from sqlalchemy.ext.asyncio import AsyncSession
from manga_sales.data_scraping.db_handle import DBWriter
from manga_sales.data_scraping.web_scraper import (
    ShosekiWeeklyScraper,
)
from manga_sales.db import AsyncDatabaseSession
from manga_sales.models import Week


class PeriodicSchedule:
    """Class for creating periodic tasks"""

    def __init__(self, app: AsyncDatabaseSession) -> None:
        self.session: Callable[[], AsyncSession] = app.get_session
        self.is_started: bool = False
        self._tasks: list[DBWriter] = [DBWriter(app, ShosekiWeeklyScraper)]

    async def start(self) -> None:
        if not self.is_started:
            self.is_started = True
            self._task = asyncio.get_event_loop().create_task(self._run())

    async def stop(self) -> None:
        if self.is_started:
            self.is_started = False
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task

    async def _run(self) -> None:
        while True:
            async with self.session() as session:
                last_date = await Week.get_last_date(
                    session,
                    self._tasks[0].scraper.SOURCE,
                    self._tasks[0].scraper.SOURCE_TYPE,
                )
            if last_date:
                last_datetime = datetime.datetime.combine(
                    last_date, datetime.datetime.min.time()
                )
                next_date = last_datetime + datetime.timedelta(days=7)
                remaining = (next_date - datetime.datetime.now()).total_seconds()
                print(remaining)
                await asyncio.sleep(remaining)
            tasks = [asyncio.create_task(task.write_data()) for task in self._tasks]
            await asyncio.gather(*tasks)
