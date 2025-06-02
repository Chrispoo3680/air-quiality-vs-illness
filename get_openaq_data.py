import sys
from pathlib import Path
import os

repo_root_dir: Path = Path().resolve()
sys.path.append(str(repo_root_dir))

from datetime import datetime
from collections import defaultdict
from tqdm import tqdm
import argparse
import pandas as pd
from typing import List

from src import openaq_api
from src.common import tools


parser = argparse.ArgumentParser(description="Hyperparameter configuration")

parser.add_argument(
    "--date-from",
    type=str,
    default="2024-1-1",
    help="Start date when fetching measurements (year-month-day).",
)
parser.add_argument(
    "--date-to",
    type=str,
    default="2025-1-1",
    help="End date when fetching measurements (year-month-day).",
)
parser.add_argument(
    "--max-sensors",
    type=int,
    default=10,
    help="The max amount of sensors to get measurements from per country.",
)


def main():

    args = parser.parse_args()

    # Setup hyperparameters
    DATE_FROM: datetime = datetime.strptime(args.date_from, "%Y-%m-%d")
    DATE_TO: datetime = datetime.strptime(args.date_to, "%Y-%m-%d")
    MAX_SENSORS_PER_COUNTRY = args.max_sensors
    COUNTRIES: List[str] = pd.read_csv("data/countries.csv")["countries"].to_list()

    logger = tools.create_logger(logger_name=__name__)

    config = tools.load_config()

    logger.debug(
        f"Using hyperparameters:"
        f"\n    date_from = {DATE_FROM.isoformat()}"
        f"\n    date_to = {DATE_TO.isoformat()}"
        f"\n    max_sensors_per_country = {MAX_SENSORS_PER_COUNTRY}"
        f"\n    country = {COUNTRIES}"
    )

    # Convert country names into iso alpha-2 codes
    logger.info(f"Getting iso alpha-2 codes for countries...")

    iso_codes: List[str] = tools.get_alpha2_iso_codes(COUNTRIES)

    # Getting locations ids for all locations in chosen countries
    logger.info(f"Getting location ids...")

    country_locations = openaq_api.get_locations(
        iso_codes, date_from=DATE_FROM, date_to=DATE_TO
    )

    logger.info(f"Successfully fetched location ids!")

    sensor_parameters: List[str] = ["pm1", "pm10", "pm25", "no2", "o3", "so2", "co"]
    MAX_SENSORS_PER_COUNTRY = 10

    sensor_measurements = defaultdict(dict)

    for country, locations in tqdm(
        country_locations.items(),
        position=1,
        leave=False,
        desc=f"Iterating though countries",
    ):
        filtered_sensors = openaq_api.filter_sensors(
            locations, max_amount=MAX_SENSORS_PER_COUNTRY, parameters=sensor_parameters
        )

        for parameter, sensors in tqdm(
            filtered_sensors.items(),
            position=2,
            leave=False,
            desc=f"Getting sensor measurements for country '{country}'",
        ):
            measurements = [
                openaq_api.get_sensor_measurements(
                    sensor["id"], date_from=DATE_FROM, date_to=DATE_TO
                )
                for sensor in sensors
            ]

            sensor_measurements[country][parameter] = tools.average(measurements)

    sensor_measurements = [
        dict(country=country, **measurements)
        for country, measurements in sensor_measurements.items()
    ]

    # Saving sensor measurements to .csv file
    save_path: Path = repo_root_dir / config["data_path"] / "openaq_data.csv"
    os.makedirs(save_path.parent, exist_ok=True)

    logger.info(f"Saving sensor measurements to file: {save_path}")
    tools.save_dict_to_csv(sensor_measurements, save_path)


if __name__ == "__main__":
    main()
