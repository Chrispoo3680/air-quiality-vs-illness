import sys
from pathlib import Path
import os

repo_root_dir: Path = Path().resolve()
sys.path.append(str(repo_root_dir))

from datetime import datetime
from collections import defaultdict
from tqdm import tqdm

from src import openaq_api
from src.common import tools


def main():

    logger = tools.create_logger(logger_name=__name__)

    config = tools.load_config()

    countries = ["Norway", "Japan", "United Kingdom"]
    date_from = datetime(2024, 1, 1)
    date_to = datetime(2025, 1, 1)

    # Convert country names into iso alpha-2 codes
    logger.info(f"Getting iso alpha-2 codes for countries:\n{countries}")

    iso_codes = openaq_api.get_iso_country_codes(countries)

    # Getting locations ids for all locations in chosen countries
    logger.info(f"Getting location ids...")
    logger.debug(
        f"Fetching locations with measurements between dates '{date_from.isoformat()}' and '{date_to.isoformat()}'."
    )

    country_locations = openaq_api.get_locations(
        iso_codes, date_from=date_from, date_to=date_to
    )

    logger.info(f"Successfully fetched location ids!")

    sensor_parameters = ["pm25", "pm10", "no2"]
    max_sensors_per_country = 5
    sensor_measurements = defaultdict(dict)

    for country, locations in tqdm(
        country_locations.items(),
        leave=False,
        position=1,
        desc=f"Iterating though countries",
    ):
        filtered_sensors = openaq_api.filter_sensors(
            locations, max_amount=max_sensors_per_country, parameters=sensor_parameters
        )

        for parameter, sensors in tqdm(
            filtered_sensors.items(),
            leave=False,
            position=1,
            desc=f"Getting sensor measurements for country '{country}'",
        ):
            measurements = [
                openaq_api.get_sensor_measurements(
                    sensor["id"], date_from=date_from, date_to=date_to
                )
                for sensor in sensors
            ]

            sensor_measurements[country][parameter] = round(
                sum(measurements) / len(measurements), 3
            )

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
