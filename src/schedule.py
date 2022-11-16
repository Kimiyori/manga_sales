import aioschedule as schedule
from src.data_scraping.services.db_service import execute_scraper


async def run_schedule() -> None:
    schedule.every(5).minutes.do(execute_scraper, scraper_name="oricon_scraper")
    # schedule.every(3).minutes.do(execute_scraper, scraper_name="shoseki_scraper")
    await schedule.run_all()
