import asyncio
from manga_scrapers.services.db_service import execute_scraper


async def run_schedule() -> None:
    tasks = [
        asyncio.create_task(execute_scraper(scraper_name))
        for scraper_name in ["oricon_scraper", "shoseki_scraper"]
    ]
    asyncio.gather(*tasks)
