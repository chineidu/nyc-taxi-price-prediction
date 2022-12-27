from src.predict import make_predictions as make_predictions
from src.processing.data_manager import _set_up_logger as logger
from src.processing.data_manager import load_data as load_data
from src.processing.data_manager import load_model as load_model
from src.processing.data_manager import load_version as load_version

__version__ = load_version()
VERSION = "0.0.1"
