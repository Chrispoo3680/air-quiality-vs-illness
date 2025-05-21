import yaml
from pathlib import Path


def load_config():
    # Read in the configuration file
    with open("../../config.yaml") as p:  # Might need a better solution in the future
        config = yaml.safe_load(p)
    return config
