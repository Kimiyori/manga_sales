import asyncio
from contextlib import suppress
import datetime
from manga_sales.data_scraping.db_handle import DBWriter
from manga_sales.data_scraping.web_scraper import OriconScraper
from manga_sales.models import Week


class PeriodicSchedule:
    def __init__(self, app):
        self.session= app.get_session
        self.is_started = False
        self._tasks = [DBWriter(app, OriconScraper)]

    async def start(self):
        if not self.is_started:
            self.is_started = True
            self._task = asyncio.get_event_loop().create_task(self._run())

    async def stop(self):
        if self.is_started:
            self.is_started = False
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task

    async def _run(self):
        while True:
            async with self.session() as session:
                last_date = await Week.get_last_date(session)
            last_date=datetime.datetime.combine(last_date, datetime.datetime.min.time())
            next_date=last_date+datetime.timedelta(days=7)
            remaining= (next_date-datetime.datetime.now()).total_seconds()
            await asyncio.sleep( remaining)
            tasks = [asyncio.create_task(task.write_data())
                     for task in self._tasks]
            await asyncio.gather(*tasks)
