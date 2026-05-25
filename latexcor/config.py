from pathlib import Path

import yaml


def load_config():
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, "r") as config_file:
        return yaml.safe_load(config_file)


config = load_config()

CLEAN_UP_EXTENSIONS = config["clean_up_extensions"]
CLEAN_PATHS = config["clean_paths"]
WATCH_COOLDOWN = 2
