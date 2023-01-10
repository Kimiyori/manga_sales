import datetime
import re


def convert_str_to_date(date: str, pattern: str) -> datetime.date:
    """Convert string date to datetime.date type

    Args:
        date (str): The method accepts the following date patterns:%Y(-/.)%m(-/.)%d,
        else throws error

    Returns:
        datetime.date: if day not passed, then it set default to 1
    """
    str_date = re.search(pattern, date)
    assert str_date is not None, "Fail match date"
    return datetime.datetime.strptime(
        (
            f'{str_date["year"]}/'
            f'{str_date["month"]}/'
            f'{str_date["day"] if str_date["day"] else 1}'
        ),
        "%Y/%m/%d",
    ).date()
