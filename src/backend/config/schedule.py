import aioschedule as schedule
from manga_scrapers.services.db_service import execute_scraper


async def run_schedule() -> None:
    schedule.every().thursday.do(run_scrapers)
    await schedule.run_all()


async def run_scrapers() -> None:
    scraper_names = ["oricon_scraper", "shoseki_scraper"]
    for name in scraper_names:
        await execute_scraper(name)
    # tasks = [
    #     asyncio.create_task(execute_scraper(scraper_name))
    #     for scraper_name in ["oricon_scraper", "shoseki_scraper"]
    # ]
    # asyncio.gather(*tasks)
