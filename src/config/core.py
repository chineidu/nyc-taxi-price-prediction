import yaml

# Custom Imports
from schema import MLFlowConfig, ConfigVars, ModelConfig
import src

import typing as tp
from pathlib import Path

SRC_DIR = Path(src.__file__).absolute().parent
ROOT_DIR = SRC_DIR.parent
CONFIG_FILEPATH = SRC_DIR / "config.yml"
DATA_FILEPATH = SRC_DIR / "data"
TRAINED_MODELS_FILEPATH = SRC_DIR / "models"


def load_yaml_file(*, filename: tp.Optional[Path] = None) -> tp.Dict:
    """This loads the YAML file as a dict"""
    if filename is None:
        filename = CONFIG_FILEPATH

    with open(filename, "r") as file:
        config_dict = yaml.safe_load(stream=file)
    return config_dict


def validate_config_file(*, filename: tp.Optional[Path] = None) -> ConfigVars:
    """This loads the config as a Pydantic object."""
    config_dict = load_yaml_file(filename)

    config_file = ConfigVars(
        model_config=ModelConfig(**config_dict),
        mlflow_config=MLFlowConfig(**config_dict),
    )
    return config_file


config = validate_config_file(filename=None)
