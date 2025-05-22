import requests
import pycountry

from .common.tools import load_config
from collections import defaultdict

from datetime import datetime

from typing import List, Dict


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

    endpoint = f"{config["openaq_api_url"]}locations"
    headers = headers = {"X-API-Key": config["openaq_api_key"]}

    format_string = "%Y-%m-%dT%H:%M:%SZ"

    locations = defaultdict(list)

    for iso in iso_codes:
        page = 1
        retrieved = False

        while not retrieved:
            params = {"iso": iso, "limit": limit, "page": page}

            response = requests.get(endpoint, params=params, headers=headers)
            response_json = response.json()

            for loc in response_json["results"]:

                if loc["datetimeFirst"] is None or loc["datetimeLast"] is None:
                    continue
                elif (
                    datetime.strptime(loc["datetimeFirst"]["utc"], format_string)
                    < date_from
                    and datetime.strptime(loc["datetimeLast"]["utc"], format_string)
                    > date_to
                ):
                    locations[loc["country"]["code"]].append(loc)

            if response_json["meta"]["found"] != f">{limit}":
                retrieved = True

            page += 1

    return dict(locations)


def filter_sensors(locations, max_amount):

    filtered = defaultdict(list)

    for location in locations:
        for sensor in location["sensors"]:

            if len(filtered[sensor["parameter"]["name"]]) >= max_amount:
                filtered[sensor["parameter"]["name"]].append(
                    dict(
                        coordinates=location["coordinates"],
                        datetimeFirst=location["datetimeFirst"],
                        datetimeLast=location["datetimeLast"],
                        **sensor,
                    )
                )
