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

    # Confirm it's stored on S3
    logger.info(mlflow.get_artifact_uri())



# ==== Make Predictions Suding The Model From The Model Registry ====
import pandas as pd
from pprint import pprint as pp

# Does not depend on the tracking server
RUN_ID = "98f43706f6184694be1ee10c41c7b69d"
S3_BUCKET_NAME = f"s3://mlflow-model-registry-neidu/1/{RUN_ID}/artifacts/model"
new_data = {
    "DOLocationID": [82, 72],
    "payment_type": [1, 2],
    "PULocationID": [5, 99],
    "RatecodeID": [np.nan, 2],
    "tpep_pickup_datetime": ["2022-12-16 14:33:43", "2022-12-18 09:18:03"],
    "trip_distance": [5.5, 3.1],
    "VendorID": [2, 1],
    "total_amount": [12, 9.5],
}

df = pd.DataFrame(new_data)
# Conevrt to datetime
df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"], errors="coerce")

# Download model artifact from S3
estimator = mlflow.pyfunc.load_model(model_uri=f"{S3_BUCKET_NAME}")
pp(estimator.predict(df))
