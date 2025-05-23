import yaml
from pathlib import Path
import csv

from typing import Dict, Union, List


def load_config():
    # Read in the configuration file
    with open("config.yaml") as p:  # Might need a better solution in the future
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
        w.writerow(data)  # type: ignore
