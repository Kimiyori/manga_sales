import datetime
from pathlib import Path


def convert_date(date: str, type: str) -> str:
    try:
        datetime_object = datetime.datetime.strptime(date, "%B")
        date_part: int = getattr(datetime_object, type)
    except TypeError:
        date_part = int(date)
    return str(date_part) if date_part > 9 else f"0{date_part}"


def file_exist(date: datetime.date, name: str) -> bool:
    date_str = date.strftime("%Y-%m-%d")
    if Path(f"manga_sales/static/images/oricon/{date_str}/{name}").is_file():
        return True
    return False
