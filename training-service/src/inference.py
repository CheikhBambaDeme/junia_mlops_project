"""
inference.py - Inference Script
=================================
Separate inference module with explicit model loading.
Used by the FastAPI endpoints to make predictions.
"""

import os
import logging
import pandas as pd
import numpy as np
from src.train import load_model
from src.model import preprocess_features

logger = logging.getLogger(__name__)


class HousingPredictor:
    """
    Inference wrapper that loads the model once and serves predictions.
    The model is loaded explicitly at initialization.
    """

    def __init__(self, model_dir="/app/models/artifacts", model_name=None):
        """
        Load model explicitly at initialization.
        
        Args:
            model_dir: Path to the directory containing model artifacts
            model_name: Base name of the model (from env or default)
        """
        self.model_dir = model_dir
        self.model_name = model_name or os.getenv(
            "MODEL_NAME", "housing_price_predictor"
        )
        self.model = None
        self.feature_info = None
        self.is_loaded = False

        self._load()

    def _load(self):
        """Explicitly load the model and metadata from disk."""
        try:
            self.model, self.feature_info = load_model(
                self.model_dir, self.model_name
            )
            self.is_loaded = True
            logger.info(
                f"✅ Predictor ready — model version: {self.feature_info['timestamp']}"
            )
        except FileNotFoundError as e:
            logger.warning(f"⚠️ Model not found, predictor not ready: {e}")
            self.is_loaded = False
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}", exc_info=True)
            self.is_loaded = False

    def reload(self):
        """Reload model from disk (e.g. after retraining)."""
        logger.info("Reloading model...")
        self._load()

    def predict(self, features: dict) -> dict:
        """
        Make a prediction from raw feature dict.
        
        Args:
            features: dict with keys like
                {
                    "Bedrooms": 3,
                    "Bathrooms": 2,
                    "SquareFeet": 1800,
                    "Location": "Chicago"
                }
        
        Returns:
            dict with prediction, model_version, features_used
        
        Raises:
            RuntimeError: If model is not loaded
            ValueError: If features are invalid
        """
        if not self.is_loaded:
            raise RuntimeError("Model is not loaded. Train a model first.")

        label_encoder = self.feature_info["label_encoder"]
        feature_names = self.feature_info["feature_names"]

        # Encode Location if present
        if "Location" in features:
            try:
                features["Location_encoded"] = float(
                    label_encoder.transform([features["Location"]])[0]
                )
            except ValueError:
                valid = list(label_encoder.classes_)
                raise ValueError(
                    f"Unknown location '{features['Location']}'. Valid: {valid}"
                )
            # Remove the raw Location key
            features.pop("Location", None)

        # Build DataFrame in the correct column order
        input_df = pd.DataFrame([features])

        # Ensure all expected features are present
        missing = set(feature_names) - set(input_df.columns)
        if missing:
            raise ValueError(f"Missing features: {missing}")

        input_df = input_df[feature_names].astype(float)

        prediction = self.model.predict(input_df)[0]

        return {
            "prediction": float(prediction),
            "model_version": self.feature_info["timestamp"],
            "features_used": feature_names,
        }
