import yaml
from pathlib import Path
import sys


def load_config():
    # Read in the configuration file
    with open(
        Path(sys.path[-1]) / "config.yaml"  # Might need a better solution in the future
    ) as p:
        config = yaml.safe_load(p)
    return config
