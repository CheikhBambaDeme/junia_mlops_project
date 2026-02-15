"""
validate_data.py - Data Validation
====================================
Validates input data schema and constraints using Pandera.
Ensures data quality before training or inference.
"""

import pandera as pa
from pandera import Column, Check, DataFrameSchema
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# ---- Schema definition for the raw housing dataset ----
HOUSING_SCHEMA = DataFrameSchema(
    {
        "HouseID": Column(int, Check.greater_than(0), nullable=False),
        "Location": Column(
            str,
            Check.isin(["New York", "Los Angeles", "Chicago", "Houston"]),
            nullable=False,
        ),
        "Bedrooms": Column(int, Check.in_range(1, 10), nullable=False),
        "Bathrooms": Column(int, Check.in_range(1, 5), nullable=False),
        "SquareFeet": Column(
            int, Check.in_range(100, 10000), nullable=False
        ),
        "Price": Column(float, Check.greater_than(0), nullable=False),
    },
    strict=False,  # Allow extra columns without failing
    coerce=True,   # Coerce types automatically
)

# ---- Schema for inference input (no Price, no HouseID) ----
INFERENCE_SCHEMA = DataFrameSchema(
    {
        "Location": Column(
            str,
            Check.isin(["New York", "Los Angeles", "Chicago", "Houston"]),
            nullable=False,
        ),
        "Bedrooms": Column(int, Check.in_range(1, 10), nullable=False),
        "Bathrooms": Column(int, Check.in_range(1, 5), nullable=False),
        "SquareFeet": Column(
            int, Check.in_range(100, 10000), nullable=False
        ),
    },
    strict=False,
    coerce=True,
)


def validate_housing_data(df: pd.DataFrame) -> bool:
    """
    Validate the full training dataset.
    
    Args:
        df: DataFrame loaded from the raw CSV
    
    Returns:
        True if validation passes
    
    Raises:
        pandera.errors.SchemaError: If validation fails
    """
    try:
        HOUSING_SCHEMA.validate(df)
        logger.info(
            f"✅ Data validation passed — {len(df)} rows, "
            f"{len(df.columns)} columns"
        )
        return True
    except pa.errors.SchemaError as e:
        logger.error(f"❌ Data validation failed:\n{e}")
        raise


def validate_inference_input(df: pd.DataFrame) -> bool:
    """
    Validate inference input data (single or batch predictions).
    
    Args:
        df: DataFrame with prediction features
    
    Returns:
        True if validation passes
    
    Raises:
        pandera.errors.SchemaError: If validation fails
    """
    try:
        INFERENCE_SCHEMA.validate(df)
        logger.info("✅ Inference input validation passed")
        return True
    except pa.errors.SchemaError as e:
        logger.error(f"❌ Inference input validation failed:\n{e}")
        raise
