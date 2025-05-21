import requests
import pycountry

from .common.tools import load_config
from collections import defaultdict

from typing import List, Dict


def get_iso_country_codes(country_names: List[str]) -> List[str]:

    country_dict: Dict[str, str] = {
        country.name: country.alpha_2 for country in list(pycountry.countries)  # type: ignore
    }

    filtered_iso_codes: List[str] = [country_dict[name] for name in country_names]

    return filtered_iso_codes


def get_location_ids(iso_codes: List[str], limit=100):

    config = load_config()

    endpoint = f"{config["openaq_api_url"]}locations"
    headers = headers = {"X-API-Key": config["openaq_api_key"]}

    locations = defaultdict(list)

    for iso in iso_codes:
        params = {"iso": iso, "limit": limit}
        response = requests.get(endpoint, params=params, headers=headers)

        for loc in response.json()["results"]:
            locations[loc["country"]["code"]].append(loc)

    return locations
