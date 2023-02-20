import aioschedule as schedule
from manga_scrapers.services.db_service import execute_scraper


async def run_schedule() -> None:
    schedule.every(55).minutes.do(execute_scraper, scraper_name="oricon_scraper")
    # schedule.every(55).minutes.do(execute_scraper, scraper_name="shoseki_scraper")
    await schedule.run_all()
