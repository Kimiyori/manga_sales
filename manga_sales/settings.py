import pathlib
from typing_extensions import reveal_type
import yaml

BASE_DIR = pathlib.Path(__file__).parent.parent
config_path = BASE_DIR / 'config' / 'polls.yaml'


def get_config(path: pathlib.Path) -> dict[str, dict[str, str]]:
    with open(path) as f:
        config: dict[str, dict[str, str]] = yaml.safe_load(f)
    return config


config = get_config(config_path)
