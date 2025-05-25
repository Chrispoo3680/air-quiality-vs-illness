import sys
from pathlib import Path
import os

repo_root_dir: Path = Path().resolve()
sys.path.append(str(repo_root_dir))

from datetime import datetime
from collections import defaultdict
from tqdm import tqdm
import argparse
from typing import List, Dict

from src import ihme_api
from src.common import tools


parser = argparse.ArgumentParser(description="Hyperparameter configuration")

parser.add_argument(
    "--indicator-id",
    type=int,
    default=1001,
    help="Id for which indicator to get data for.",
)
parser.add_argument(
    "--year",
    type=int,
    default=2024,
    help="Year to get data from.",
)
parser.add_argument(
    "--sex-id",
    type=int,
    default=3,
    help="Id for which gender to get data for.",
)
parser.add_argument(
    "--age-group-id",
    type=int,
    default=22,
    help="Id for which age group to get data for.",
)
parser.add_argument(
    "--scenario",
    type=int,
    default=0,
    help="Id for which scenario to get data for.",
)


def main():

    args = parser.parse_args()

    # Setup hyperparameters
    INDICATOR_ID: int = args.indicator_id
    YEAR: int = args.year
    SEX_ID: int = args.sex_id
    AGE_GROUP_ID: int = args.age_group_id
    SCENARIO: int = args.scenario
    COUNTRIES: List[str] = ["Norway", "Japan", "United Kingdom"]

    logger = tools.create_logger(logger_name=__name__)

    config = tools.load_config()

    logger.debug(
        f"Using hyperparameters:"
        f"\n    indicator_id = {INDICATOR_ID}"
        f"\n    year = {YEAR}"
        f"\n    sex_id = {SEX_ID}"
        f"\n    age_group_id = {AGE_GROUP_ID}"
        f"\n    scenario = {SCENARIO}"
        f"\n    country = {COUNTRIES}"
    )

    # Convert country names into iso alpha-2 codes
    logger.info(f"Getting location ids for countries...")

    location_ids: Dict[str, int] = ihme_api.get_location_ids(COUNTRIES)

    # Getting values for given target for all locations ids
    logger.info(f"Getting values for location ids...")

    values = defaultdict(float)

    for iso, id in tqdm(location_ids.items(), leave=False, position=1):
        values[iso] = ihme_api.get_target(
            location_id=id,
            indicator_id=INDICATOR_ID,
            year=YEAR,
            sex_id=SEX_ID,
            age_group_id=AGE_GROUP_ID,
            scenario=SCENARIO,
        )

    values: List[Dict[str, float]] = [
        dict(country=country, value=value) for country, value in values.items()
    ]

    # Saving sensor measurements to .csv file
    save_path: Path = repo_root_dir / config["data_path"] / "ihme_data.csv"
    os.makedirs(save_path.parent, exist_ok=True)

    logger.info(f"Saving sensor measurements to file: {save_path}")
    tools.save_dict_to_csv(values, save_path)


if __name__ == "__main__":
    main()
