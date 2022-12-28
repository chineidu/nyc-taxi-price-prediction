"""
This module is used for experiment tracking.

author: Chinedu Ezeofor
"""
# MLFlow
import mlflow

# Custom imports
from src.processing.data_manager import split_train_data
from src.pipeline import rf_pipe
from src.utilities.experiment import eval_metrics
from src import logger, config, load_data


TRACKING_SERVER_HOST = "http://127.0.0.1"  
PORT = 5000  # Default
TRACKING_URI = f"http://{TRACKING_SERVER_HOST}:{PORT}"

data = load_data(filename=config.path_config.TRAIN_DATA)
target = target = config.model_config.TARGET
test_size = config.model_config.TEST_SIZE
random_state = config.model_config.RANDOM_STATE

mlflow.set_tracking_uri(TRACKING_URI)
mlflow.set_experiment("Experiment_name")

with mlflow.start_run():
    logger.info("Training The Model ...")
    # Split data
    X_train, X_validate, y_train, y_validate = split_train_data(
        data=data, target=target, test_size=test_size, random_state=random_state
    )

    rf_pipe.fit(X_train, y_train)

    y_pred = rf_pipe.predict(X_validate)

    (rmse, mse, mae, r2) = eval_metrics(y_validate, y_pred)

    print(f"  RMSE: {rmse}")
    print(f"  MSE: {mse}")
    print(f"  MAE: {mae}")
    print(f"  R2: {r2}")

    mlflow.log_metrics({"RMSE": rmse, "MSE": mse, "MAE": mae, "R2": r2})

    mlflow.sklearn.log_model(
        rf_pipe, artifact_path="model", registered_model_name="LinearModel"
    )
    logger.info("Training Done! ...")
