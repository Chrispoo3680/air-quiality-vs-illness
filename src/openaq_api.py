import requests
import pycountry
from collections import defaultdict
from datetime import datetime
import random
import logging

from .common import tools

from typing import List, Dict, Union


if __name__ in logging.Logger.manager.loggerDict:
    logger = logging.getLogger(__name__)
else:
    logger = tools.create_logger(logger_name=__name__)


def get_locations(
    iso_codes: List[str], date_from: datetime, date_to: datetime, limit: int = 1000
) -> Dict[str, List]:

    config = tools.load_config()

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

            if response.status_code == 429:
                logger.info(
                    "API request rate exceeded! Waiting 1 minute before trying another GET request."
                )
                tools.countdown(60)
                logger.info("Trying to send a new GET request to API.")

            elif response.status_code == 200:
                response_json: Dict = response.json()

                for loc in response_json["results"]:

                    if loc["datetimeFirst"] is None or loc["datetimeLast"] is None:
                        continue
                    elif (
                        datetime.fromisoformat(loc["datetimeFirst"]["local"]).replace(
                            tzinfo=None
                        )
                        <= date_from
                        and datetime.fromisoformat(
                            loc["datetimeLast"]["local"]
                        ).replace(tzinfo=None)
                        >= date_to
                    ):
                        locations[loc["country"]["code"]].append(loc)

                if response_json["meta"]["found"] != f">{limit}":
                    retrieved = True

                page += 1

            else:
                logger.error(
                    f"Got response with status code '{response.status_code}' when trying to fetch location ids."
                )

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
    sensor_id: int, date_from: datetime, date_to: datetime, limit: int = 100
) -> float:

    config = tools.load_config()

    endpoint: str = f"{config["openaq_api_url"]}sensors/{sensor_id}/years"
    headers: Dict[str, str] = {"X-API-Key": config["openaq_api_key"]}
    page = 1

    values: List[float] = []

    retrieved = False

    while not retrieved:
        params: Dict[str, Union[str, int]] = {
            "limit": limit,
            "page": page,
        }

        response = requests.get(endpoint, params=params, headers=headers)

        if response.status_code == 429:
            logger.info(
                "API request rate exceeded! Waiting 1 minute before trying another GET request."
            )
            tools.countdown(60)
            logger.info("Trying to send a new GET request to API.")

        elif response.status_code == 200:
            response_json: Dict = response.json()

            for year in response_json["results"]:
                if (
                    datetime.fromisoformat(
                        year["period"]["datetimeFrom"]["local"]
                    ).replace(tzinfo=None)
                    >= date_from
                    and datetime.fromisoformat(
                        year["period"]["datetimeTo"]["local"]
                    ).replace(tzinfo=None)
                    <= date_to
                ):
                    values.append(year["value"])

            if response_json["meta"]["found"] != f">{limit}":
                retrieved = True

            page += 1

        else:
            logger.error(
                f"Got response with status code '{response.status_code}' when trying to fetch sensor measurements."
            )

    if values:
        return sum(values) / len(values)
    else:
        return -1
