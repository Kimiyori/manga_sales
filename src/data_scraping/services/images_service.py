from pathlib import Path
import shutil


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


def delete_images(source: str, source_type: str, date: str) -> None:
    # exception handler
    def handler(func, path, exc_info) -> None:  # type: ignore
        print(exc_info)

    path = (
        f"src/manga_sales/static/images/{source.lower()}/{source_type.lower()}/{date}"
    )
    # remove if exists
    shutil.rmtree(path, onerror=handler)
