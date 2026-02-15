"""
model.py - Model Architecture & Preprocessing
===============================================
Defines the model architecture and feature preprocessing pipeline.
This is intentionally separated so changes here trigger CI/CD retraining.

Last updated: 2026-02-15 — initial pipeline test
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import logging

logger = logging.getLogger(__name__)


def create_model(n_estimators=100, max_depth=15, random_state=42, **kwargs):
    """
    Create and return the model architecture.
    
    Changing this function's parameters or model type should trigger
    a retraining pipeline via GitHub Actions.
    
    Args:
        n_estimators: Number of trees in the forest
        max_depth: Maximum depth of each tree
        random_state: Random seed for reproducibility
    
    Returns:
        sklearn model instance (unfitted)
    """
    logger.info(
        f"Creating RandomForestRegressor with n_estimators={n_estimators}, "
        f"max_depth={max_depth}, random_state={random_state}"
    )
    return RandomForestRegressor(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=random_state,
        n_jobs=-1
    )


def preprocess_features(df):
    """
    Preprocess features for housing price prediction.
    
    Dataset columns: HouseID, Location, Bedrooms, Bathrooms, SquareFeet, Price
    - HouseID is dropped (not a feature)
    - Location is label-encoded (categorical -> numeric)
    - Bedrooms, Bathrooms, SquareFeet are used as-is (numeric)
    - Price is the target variable
    
    Args:
        df: Raw pandas DataFrame from the CSV
    
    Returns:
        tuple: (X features DataFrame, y target Series, label_encoder for Location)
    """
    logger.info(f"Preprocessing {len(df)} rows...")
    
    # Make a copy to avoid modifying the original
    data = df.copy()
    
    # Extract target
    y = data["Price"].astype(float)
    
    # Encode the Location column (categorical -> numeric)
    le = LabelEncoder()
    data["Location_encoded"] = le.fit_transform(data["Location"])
    logger.info(f"Location classes: {list(le.classes_)}")
    
    # Select feature columns
    feature_cols = ["Bedrooms", "Bathrooms", "SquareFeet", "Location_encoded"]
    X = data[feature_cols].astype(float)
    
    # Handle any missing values
    if X.isnull().any().any():
        logger.warning("Missing values detected, filling with median")
        X = X.fillna(X.median())
    
    logger.info(f"Features shape: {X.shape}, Target shape: {y.shape}")
    
    return X, y, le
