import yaml
from pathlib import Path
import sys
import csv
import logging
from tqdm import tqdm
import time
import pycountry

from typing import Dict, Union, List, Optional


def get_alpha2_iso_codes(country_names: List[str]) -> List[str]:

    country_dict: Dict[str, str] = {
        country.name: country.alpha_2 for country in list(pycountry.countries)  # type: ignore
    }

    filtered_iso_codes: List[str] = [country_dict[name] for name in country_names]

    return filtered_iso_codes


def average(l, decimal_points=3):
    l = list(filter(None, l))

    if len(l) > 0:
        return round(sum(l) / len(l), decimal_points)
    else:
        return None


def load_config():
    # Read in the configuration file
    with open(
        Path(sys.path[-1]) / "config.yaml"  # Might need a better solution in the future
    ) as p:
        config = yaml.safe_load(p)
    return config


def save_dict_to_csv(data: List[Dict], path: Union[Path, str]):

    fieldnames = set()
    for entry in data:
        fieldnames.update(entry.keys())
    fieldnames = list(fieldnames)

    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(data)


def countdown(t):
    while t:
        mins, secs = divmod(t, 60)
        timer = "{:02d}:{:02d}".format(mins, secs)
        tqdm.write(timer, end="\r")  # Overwrite the line each second
        time.sleep(1)
        t -= 1


def create_logger(
    logger_name: str, log_path: Optional[Union[str, Path]] = None
) -> logging.Logger:

    config = load_config()

    level_dict = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
    }

    # Set up logging
    logger = logging.getLogger(logger_name)
    logger.setLevel(level_dict[config["logging_level"]])

    # Tqdm handler for terminal output
    tqdm_handler = TqdmLoggingHandler()
    tqdm_handler.setFormatter(
        logging.Formatter("%(asctime)s  -  %(name)s  -  %(levelname)s:    %(message)s")
    )
    logger.addHandler(tqdm_handler)

    # File handler for .log file output
    if log_path:
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s  -  %(name)s  -  %(levelname)s:    %(message)s"
            )
        )
        logger.addHandler(file_handler)

    return logger


class TqdmLoggingHandler(logging.Handler):
    def emit(self, record) -> None:
        msg: str = self.format(record)
        tqdm.write(msg)
