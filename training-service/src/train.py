"""
train.py - Training Script
============================
Complete training pipeline with:
- Data loading & validation
- Feature preprocessing
- Model training with MLflow experiment tracking
- Explicit model saving (joblib) with versioning
- Metrics logging
(test)
"""

import os
import logging
import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from math import sqrt
from datetime import datetime
import joblib
import json
from dotenv import load_dotenv

from src.validate_data import validate_housing_data
from src.model import create_model, preprocess_features

load_dotenv()

# ---- Logging setup ----
os.makedirs("/app/logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/app/logs/training.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def save_model(model, label_encoder, feature_names, metrics, model_dir, model_name):
    """
    Explicitly save model artifacts to disk.
    
    Saves:
        - Timestamped model file (for versioning)
        - 'latest' model file (for inference startup)
        - Model info file (features, metrics, encoder, timestamp)
    
    Args:
        model: Trained sklearn model
        label_encoder: Fitted LabelEncoder for Location
        feature_names: List of feature column names
        metrics: Dict of evaluation metrics
        model_dir: Directory to save into
        model_name: Base name for the model files
    
    Returns:
        dict with paths and timestamp
    """
    os.makedirs(model_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Versioned path + latest symlink-style copy
    model_path = os.path.join(model_dir, f"{model_name}_{timestamp}.joblib")
    latest_path = os.path.join(model_dir, f"{model_name}_latest.joblib")

    joblib.dump(model, model_path)
    joblib.dump(model, latest_path)
    logger.info(f"Model saved → {model_path}")
    logger.info(f"Latest model → {latest_path}")

    # Save metadata (feature names, label encoder, metrics)
    info = {
        "feature_names": feature_names,
        "timestamp": timestamp,
        "metrics": metrics,
        "label_encoder": label_encoder,
        "model_params": model.get_params(),
    }
    info_path = os.path.join(model_dir, f"{model_name}_info.joblib")
    joblib.dump(info, info_path)
    logger.info(f"Model info → {info_path}")

    return {"model_path": model_path, "latest_path": latest_path, "timestamp": timestamp}


def load_model(model_dir, model_name):
    """
    Explicitly load model artifacts from disk.
    
    Args:
        model_dir: Directory containing model files
        model_name: Base name for the model files
    
    Returns:
        tuple: (model, feature_info dict)
    
    Raises:
        FileNotFoundError: If model files don't exist
    """
    model_path = os.path.join(model_dir, f"{model_name}_latest.joblib")
    info_path = os.path.join(model_dir, f"{model_name}_info.joblib")

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}")
    if not os.path.exists(info_path):
        raise FileNotFoundError(f"Model info not found at {info_path}")

    model = joblib.load(model_path)
    info = joblib.load(info_path)
    logger.info(f"Model loaded from {model_path}")
    logger.info(f"Model timestamp: {info['timestamp']}, metrics: {info['metrics']}")

    return model, info


def train_model():
    """
    Complete training pipeline.
    
    Steps:
        1. Load CSV data
        2. Validate with Pandera
        3. Preprocess features
        4. Train / test split
        5. Train model
        6. Evaluate & compute metrics
        7. Log everything to MLflow
        8. Save model explicitly with joblib
    
    Returns:
        dict with status, model_path, metrics, timestamp
    """
    try:
        # ---- Configuration from environment ----
        data_path = os.getenv("DATA_PATH", "/app/data/raw/house_prices.csv")
        model_name = os.getenv("MODEL_NAME", "housing_price_predictor")
        random_seed = int(os.getenv("RANDOM_SEED", 42))
        test_size = float(os.getenv("TEST_SIZE", 0.2))
        n_estimators = int(os.getenv("N_ESTIMATORS", 100))
        max_depth = int(os.getenv("MAX_DEPTH", 15))

        logger.info("=" * 60)
        logger.info("STARTING TRAINING PIPELINE")
        logger.info("=" * 60)

        # ---- Step 1: Load data ----
        logger.info(f"Loading data from {data_path}")
        df = pd.read_csv(data_path)
        logger.info(f"Loaded {len(df)} rows, columns: {list(df.columns)}")

        # ---- Step 2: Validate data ----
        logger.info("Validating data schema...")
        validate_housing_data(df)

        # ---- Step 3: Preprocess ----
        X, y, label_encoder = preprocess_features(df)

        # ---- Step 4: Split ----
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_seed
        )
        logger.info(f"Train set: {X_train.shape}, Test set: {X_test.shape}")

        # ---- Step 5 & 6: MLflow tracking ----
        mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "file:///app/mlruns"))
        mlflow.set_experiment(os.getenv("MLFLOW_EXPERIMENT_NAME", "housing_price_prediction"))

        with mlflow.start_run(
            run_name=f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        ):
            # Log parameters
            params = {
                "n_estimators": n_estimators,
                "max_depth": max_depth,
                "random_state": random_seed,
                "test_size": test_size,
                "dataset_rows": len(df),
                "n_features": X.shape[1],
            }
            mlflow.log_params(params)

            # Train
            logger.info("Training model...")
            model = create_model(
                n_estimators=n_estimators,
                max_depth=max_depth,
                random_state=random_seed,
            )
            model.fit(X_train, y_train)
            logger.info("Training complete.")

            # Evaluate
            y_pred = model.predict(X_test)
            metrics = {
                "rmse": float(sqrt(mean_squared_error(y_test, y_pred))),
                "mae": float(mean_absolute_error(y_test, y_pred)),
                "r2": float(r2_score(y_test, y_pred)),
            }
            logger.info(f"Metrics: {json.dumps(metrics, indent=2)}")
            mlflow.log_metrics(metrics)

            # Log model to MLflow registry
            mlflow.sklearn.log_model(model, "model")

            # ---- Step 7: Explicit save ----
            model_dir = "/app/models/artifacts"
            save_result = save_model(
                model=model,
                label_encoder=label_encoder,
                feature_names=list(X.columns),
                metrics=metrics,
                model_dir=model_dir,
                model_name=model_name,
            )

            logger.info("=" * 60)
            logger.info("TRAINING PIPELINE COMPLETED SUCCESSFULLY")
            logger.info("=" * 60)

            return {
                "status": "success",
                "model_path": save_result["model_path"],
                "metrics": metrics,
                "timestamp": save_result["timestamp"],
                "params": params,
            }

    except Exception as e:
        logger.error(f"Training failed: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    result = train_model()
    print(f"\nTraining completed: {json.dumps(result, indent=2)}")
