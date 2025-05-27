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
    "--indicator-ids",
    type=int,
    default=[
        1000,
        1001,
    ],
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
    INDICATOR_IDS: List[int] = args.indicator_ids
    YEAR: int = args.year
    SEX_ID: int = args.sex_id
    AGE_GROUP_ID: int = args.age_group_id
    SCENARIO: int = args.scenario
    COUNTRIES: List[str] = [
        "Afghanistan",
        "Albania",
        "Algeria",
        "American Samoa",
        "Andorra",
        "Angola",
        "Antigua and Barbuda",
        "Argentina",
        "Armenia",
        "Australia",
        "Austria",
        "Azerbaijan",
        "Bahamas",
        "Bahrain",
        "Bangladesh",
        "Barbados",
        "Belarus",
        "Belgium",
        "Belize",
        "Benin",
        "Bermuda",
        "Bhutan",
        "Bosnia and Herzegovina",
        "Botswana",
        "Brazil",
        "Brunei Darussalam",
        "Bulgaria",
        "Burkina Faso",
        "Burundi",
        "Cabo Verde",
        "Cambodia",
        "Cameroon",
        "Canada",
        "Central African Republic",
        "Chad",
        "Chile",
        "China",
        "Colombia",
        "Comoros",
        "Congo",
        "Cook Islands",
        "Costa Rica",
        "Croatia",
        "Cuba",
        "Cyprus",
        "Czechia",
        "Côte d'Ivoire",
        "Denmark",
        "Djibouti",
        "Dominica",
        "Dominican Republic",
        "Ecuador",
        "Egypt",
        "El Salvador",
        "Equatorial Guinea",
        "Eritrea",
        "Estonia",
        "Eswatini",
        "Ethiopia",
        "Fiji",
        "Finland",
        "France",
        "Gabon",
        "Gambia",
        "Georgia",
        "Germany",
        "Ghana",
        "Greece",
        "Greenland",
        "Grenada",
        "Guam",
        "Guatemala",
        "Guinea",
        "Guinea-Bissau",
        "Guyana",
        "Haiti",
        "Honduras",
        "Hungary",
        "Iceland",
        "India",
        "Indonesia",
        "Iraq",
        "Ireland",
        "Israel",
        "Italy",
        "Jamaica",
        "Japan",
        "Jordan",
        "Kazakhstan",
        "Kenya",
        "Kiribati",
        "Kuwait",
        "Kyrgyzstan",
        "Lao People's Democratic Republic",
        "Latvia",
        "Lebanon",
        "Lesotho",
        "Liberia",
        "Libya",
        "Lithuania",
        "Luxembourg",
        "Madagascar",
        "Malawi",
        "Malaysia",
        "Maldives",
        "Mali",
        "Malta",
        "Marshall Islands",
        "Mauritania",
        "Mauritius",
        "Mexico",
        "Mongolia",
        "Montenegro",
        "Morocco",
        "Mozambique",
        "Myanmar",
        "Namibia",
        "Nauru",
        "Nepal",
        "Netherlands",
        "New Zealand",
        "Nicaragua",
        "Niger",
        "Nigeria",
        "Niue",
        "North Macedonia",
        "Northern Mariana Islands",
        "Norway",
        "Oman",
        "Pakistan",
        "Palau",
        "Panama",
        "Papua New Guinea",
        "Paraguay",
        "Peru",
        "Philippines",
        "Poland",
        "Portugal",
        "Puerto Rico",
        "Qatar",
        "Romania",
        "Russian Federation",
        "Rwanda",
        "Saint Kitts and Nevis",
        "Saint Lucia",
        "Saint Vincent and the Grenadines",
        "Samoa",
        "San Marino",
        "Sao Tome and Principe",
        "Saudi Arabia",
        "Senegal",
        "Serbia",
        "Seychelles",
        "Sierra Leone",
        "Singapore",
        "Slovakia",
        "Slovenia",
        "Solomon Islands",
        "Somalia",
        "South Africa",
        "South Sudan",
        "Spain",
        "Sri Lanka",
        "Sudan",
        "Suriname",
        "Sweden",
        "Switzerland",
        "Syrian Arab Republic",
        "Tajikistan",
        "Thailand",
        "Timor-Leste",
        "Togo",
        "Tokelau",
        "Tonga",
        "Trinidad and Tobago",
        "Tunisia",
        "Turkmenistan",
        "Tuvalu",
        "Uganda",
        "Ukraine",
        "United Arab Emirates",
        "United Kingdom",
        "Uruguay",
        "Uzbekistan",
        "Vanuatu",
        "Viet Nam",
        "Yemen",
        "Zambia",
        "Zimbabwe",
    ]

    logger = tools.create_logger(logger_name=__name__)

    config = tools.load_config()

    logger.debug(
        f"Using hyperparameters:"
        f"\n    indicator_ids = {INDICATOR_IDS}"
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

    values = defaultdict(defaultdict)

    for iso, id in tqdm(location_ids.items(), leave=False, position=1):
        for indicator_id in tqdm(INDICATOR_IDS, leave=False, position=2):
            indicator_name = ihme_api.get_indicator_name(indicator_id)

            values[iso][indicator_name] = ihme_api.get_target(
                location_id=id,
                indicator_id=indicator_id,
                year=YEAR,
                sex_id=SEX_ID,
                age_group_id=AGE_GROUP_ID,
                scenario=SCENARIO,
            )

    values: List[Dict[str, float]] = [
        dict(country=country, **values) for country, values in values.items()
    ]

    # Saving sensor measurements to .csv file
    save_path: Path = repo_root_dir / config["data_path"] / "ihme_data.csv"
    os.makedirs(save_path.parent, exist_ok=True)

    logger.info(f"Saving sensor measurements to file: {save_path}")
    tools.save_dict_to_csv(values, save_path)


if __name__ == "__main__":
    main()
