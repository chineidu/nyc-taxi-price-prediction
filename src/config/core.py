import typing as tp
from pathlib import Path

import yaml

# Custom Imports
import src
from src.config.schema import ConfigVars, ModelConfig, PathConfig

SRC_ROOT = Path(src.__file__).absolute().parent
ROOT = SRC_ROOT.parent
CONFIG_FILEPATH = SRC_ROOT / "config.yml"
DATA_FILEPATH = SRC_ROOT / "data"
TRAINED_MODELS_FILEPATH = SRC_ROOT / "models"


def load_yaml_file(*, filename: tp.Optional[Path] = None) -> tp.Dict:
    """This loads the YAML file as a dict"""
    if filename is None:
        filename = CONFIG_FILEPATH

    with open(filename, "r") as file:
        config_dict = yaml.safe_load(stream=file)
    return config_dict


def validate_config_file(*, filename: tp.Optional[Path] = None) -> ConfigVars:
    """This loads the config as a Pydantic object."""
    config_dict = load_yaml_file(filename=filename)

    # Validate config
    config_file = ConfigVars(
        model_config=ModelConfig(**config_dict),
        path_config=PathConfig(**config_dict),
    )
    return config_file


print(CONFIG_FILEPATH)
config = validate_config_file(filename=None)
