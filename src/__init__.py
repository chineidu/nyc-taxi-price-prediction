from src.predict import make_predictions as make_predictions
from src.processing.data_manager import logger as logger
from src.processing.data_manager import load_data as load_data
from src.config.core import config as config
from src.processing.data_manager import load_version as load_version

__version__ = load_version()
