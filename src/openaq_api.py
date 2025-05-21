import requests
import pycountry

from common.tools import load_config

from typing import List, Dict


def get_iso_country_codes(country_names: List[str]) -> List[int]:
    country_dict: Dict[str, int] = {
        country.name: country.numeric for country in list(pycountry.countries)
    }

    filtered_iso_codes: List[int] = [country_dict[name] for name in country_names]

    return filtered_iso_codes


def get_location_ids(iso, limit=100):
    config = load_config()

    endpoint = f"{config["openaq_api_url"]}locations"

    params = {"countries_id": [79], "limit": 100}

    response = requests.get(endpoint_locations, params=params, headers=headers)

    locations = response.json()
