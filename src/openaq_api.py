import requests
import pycountry
from collections import defaultdict
from datetime import datetime
import random

from .common.tools import load_config

from typing import List, Dict, Union


def get_iso_country_codes(country_names: List[str]) -> List[str]:

    country_dict: Dict[str, str] = {
        country.name: country.alpha_2 for country in list(pycountry.countries)  # type: ignore
    }

    filtered_iso_codes: List[str] = [country_dict[name] for name in country_names]

    return filtered_iso_codes


def get_locations(
    iso_codes: List[str], date_from: datetime, date_to: datetime, limit: int = 1000
) -> Dict[str, List]:

    config = load_config()

    endpoint: str = f"{config["openaq_api_url"]}locations"
    headers: Dict[str, str] = {"X-API-Key": config["openaq_api_key"]}

    datetime_format = "%Y-%m-%dT%H:%M:%S"

    locations = defaultdict(list)

    for iso in iso_codes:
        page = 1
        retrieved = False

        while not retrieved:
            params: Dict[str, Union[str, int]] = {
                "iso": iso,
                "limit": limit,
                "page": page,
            }

            response = requests.get(endpoint, params=params, headers=headers)
            response_json: Dict = response.json()

            for loc in response_json["results"]:

                if loc["datetimeFirst"] is None or loc["datetimeLast"] is None:
                    continue
                elif (
                    datetime.strptime(
                        loc["datetimeFirst"]["local"][:-6], datetime_format
                    )
                    <= date_from
                    and datetime.strptime(
                        loc["datetimeLast"]["local"][:-6], datetime_format
                    )
                    >= date_to
                ):
                    locations[loc["country"]["code"]].append(loc)

            if response_json["meta"]["found"] != f">{limit}":
                retrieved = True

            page += 1

    return dict(locations)


def filter_sensors(
    locations: List[Dict], max_amount: int, parameters: List[str] = []
) -> Dict[str, List]:

    sensors: Dict[str, List] = defaultdict(list)

    for loc in locations:
        for sensor in loc["sensors"]:
            parameter_name = sensor["parameter"]["name"]

            if parameter_name in parameters or not parameters:
                sensors[parameter_name].append(sensor)

    filtered_sensors: Dict[str, List] = defaultdict()

    for parameter_name, monitors in sensors.items():
        if len(monitors) <= max_amount:
            filtered_sensors[parameter_name] = monitors
        else:
            filtered_sensors[parameter_name] = random.sample(monitors, k=max_amount)

    return dict(filtered_sensors)


def get_sensor_measurements(
    sensor_id: int, date_from: datetime, date_to: datetime
) -> float:

    config = load_config()

    endpoint: str = f"{config["openaq_api_url"]}sensors/{sensor_id}/years"
    headers: Dict[str, str] = {"X-API-Key": config["openaq_api_key"]}

    datetime_format = "%Y-%m-%dT%H:%M:%S"

    response = requests.get(endpoint, headers=headers)
    response_json: Dict = response.json()

    values: List[float] = []

    for yearly_measurements in response_json["results"]:
        if (
            datetime.strptime(
                yearly_measurements["period"]["datetimeFrom"]["local"][:-6],
                datetime_format,
            )
            >= date_from
            and datetime.strptime(
                yearly_measurements["period"]["datetimeTo"]["local"][:-6],
                datetime_format,
            )
            <= date_to
        ):
            values.append(yearly_measurements["value"])

    return sum(values) / len(values)
