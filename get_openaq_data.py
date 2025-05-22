import sys
from pathlib import Path
import os

repo_root_dir: Path = Path().resolve().parent
sys.path.append(str(repo_root_dir))
repo_root_dir

from datetime import datetime

from src import openaq_api
from src.common import tools

config = tools.load_config()

countries = ["Norway"]
date_from = datetime(2024, 1, 1)
date_to = datetime(2025, 1, 1)

iso_codes = openaq_api.get_iso_country_codes(countries)

locations = openaq_api.get_locations(iso_codes, date_from=date_from, date_to=date_to)
