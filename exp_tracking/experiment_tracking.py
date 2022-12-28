# MLFlow
import mlflow
from src.pipeline import rf_pipe
from src import logger


TRACKING_SERVER_HOST = "http://127.0.0.1"  # Fill in with public DNS of the EC2 instance
PORT = 5000  # Default
TRACKING_URI = f"http://{TRACKING_SERVER_HOST}:{PORT}"


mlflow.set_tracking_uri(TRACKING_URI)
mlflow.set_experiment("Experiment_name")

with mlflow.start_run():
    logger.info("Training The Model ...")
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


