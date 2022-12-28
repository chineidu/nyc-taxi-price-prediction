"""
This module is used for experiment tracking.

summary: A local server and a remote model registry (s3) is used
for experiment tracking.

author: Chinedu Ezeofor
"""
import warnings


import mlflow
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor

# Custom imports
from src.processing.data_manager import split_train_data
from src.pipeline import rf_pipe, params
from src.utilities.experiment import eval_metrics
from src import config, load_data, logger


# S3_BUCKET_NAME = mlflow-model-registry-neidu
PORT = 5001  
TRACKING_SERVER_HOST = "http://127.0.0.1"
TRACKING_URI = f"{TRACKING_SERVER_HOST}:{PORT}"
EXPERIMENT_RUN_NAME = "Taxi-duration"

data = load_data(filename=config.path_config.TRAIN_DATA)
target = target = config.model_config.TARGET
test_size = config.model_config.TEST_SIZE
random_state = config.model_config.RANDOM_STATE
registered_model_name = "Random Forest"
tags = {"developer": "Chinedu Ezeofor", "problem_type": "Regression"}

mlflow.set_tracking_uri(TRACKING_URI)
mlflow.set_experiment(EXPERIMENT_RUN_NAME)

with mlflow.start_run():
    warnings.filterwarnings("ignore")  # Required

    mlflow.set_tags(tags)
    logger.info("Splitting the data ...")
    X_train, X_validate, y_train, y_validate = split_train_data(
        data=data, target=target, test_size=test_size, random_state=random_state
    )
    logger.info("Logging params ...")
    mlflow.log_params(params)

    logger.info("Training The Model ...")
    rf_pipe.fit(X_train, y_train)

    logger.info("Making predictions ...")
    y_pred = rf_pipe.predict(X_validate)

    logger.info("Validating the model ...")
    (rmse, mse, mae, r2) = eval_metrics(y_validate, y_pred)

    print(f"  RMSE: {rmse}")
    print(f"  MSE: {mse}")
    print(f"  MAE: {mae}")
    print(f"  R2: {r2}")

    logger.info("Logging Metrics ...")
    mlflow.log_metrics({"RMSE": rmse, "MSE": mse, "MAE": mae, "R2": r2})

    logger.info("Logging Model to S3 ...")
    mlflow.sklearn.log_model(
        rf_pipe,
        artifact_path="model",
        registered_model_name=registered_model_name,
    )
    logger.info("Experiment Done! 😎...")

    # Confirmed it's stored on S3
    logger.info(mlflow.get_artifact_uri())
