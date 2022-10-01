import datetime
from pathlib import Path
def convert_date(date,type):
    try:
        datetime_object = datetime.datetime.strptime(date, "%B")
        date = getattr(datetime_object,type)
    except TypeError:
        pass
    return f'{date}' if date>9 else f'0{date}'

def file_exist(date,name):
    print(date)
    date = date.strftime( '%Y-%m-%d')
    if Path(f'manga_sales/static/images/oricon/{date}/{name}').is_file():
        return True
    return False
