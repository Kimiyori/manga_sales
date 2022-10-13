import pathlib
import yaml

BASE_DIR = pathlib.Path(__file__).parent.parent
config_path = BASE_DIR / "config" / "polls.yaml"


def get_config(path: pathlib.Path) -> dict[str, dict[str, str]]:
    with open(path, "r", encoding="UTF-8") as file:
        config_data: dict[str, dict[str, str]] = yaml.safe_load(file)
    return config_data


config = get_config(config_path)
