import sys
from pathlib import Path
import os

repo_root_dir: Path = Path().resolve().parent
sys.path.append(str(repo_root_dir))

from datetime import datetime, timedelta
from collections import defaultdict
from pprint import pprint
from tqdm import tqdm

from src import openaq_api
from src.common import tools

config = tools.load_config()

countries = ["Norway"]
date_from = datetime(2024, 1, 1)
date_to = datetime(2025, 1, 1)

iso_codes = openaq_api.get_iso_country_codes(countries)

country_locations = openaq_api.get_locations(
    iso_codes, date_from=date_from, date_to=date_to
)


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

save_path = Path(config["data_path"]) / "openaq_data.csv"
tools.save_dict_to_csv(sensor_measurements, save_path)
