import logging
import requests
from collections import defaultdict
import pycountry

from .common import tools

from typing import List, Dict


if __name__ in logging.Logger.manager.loggerDict:
    logger = logging.getLogger(__name__)
else:
    logger = tools.create_logger(logger_name=__name__)


def get_location_ids(countries: List[str]) -> Dict[str, int]:

    config = tools.load_config()

    endpoint: str = f"{config["ihme_api_url"]}GetLocation"
    headers: Dict[str, str] = {
        "Content-Type": "application/json",
        "Authorization": config["ihme_api_key"],
    }

    response = requests.get(endpoint, headers=headers)
    response_json = response.json()

    location_ids = defaultdict(int)

    for location in response_json["results"]:

        if location["location_name"] in countries:
            iso: str = tools.get_alpha2_iso_codes([location["location_name"]])[0]
            location_ids[iso] = location["location_id"]

    return dict(location_ids)


def get_target(
    location_id: int,
    indicator_id: int,
    year: int,
    sex_id: int,
    age_group_id: int,
    scenario: int,
) -> float:

    config = tools.load_config()

    endpoint: str = f"{config["ihme_api_url"]}GetResultsByLocation"
    headers: Dict[str, str] = {
        "Content-Type": "application/json",
        "Authorization": config["ihme_api_key"],
    }
    params = {
        "location_id": location_id,
        "indicator_id": indicator_id,
        "year": year,
        "sex_id": sex_id,
        "age_group_id": age_group_id,
        "scenario": scenario,
    }

    response = requests.get(endpoint, params=params, headers=headers)
    response_json = response.json()

    results: List[Dict] = response_json["results"]

    if len(results) > 1:
        logger.warning(
            "Response had more than one result! The value from the first result will be used"
        )

    return round(float(results[0]["mean_estimate"]), 3)
