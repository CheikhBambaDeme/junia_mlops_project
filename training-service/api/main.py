"""
main.py - FastAPI Application (Training & Inference API)
=========================================================
Container 1 API: Exposes endpoints for prediction, training,
health checks, and metrics.

The model is loaded at startup via the FastAPI lifespan event.
"""

import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from dotenv import load_dotenv

from src.inference import HousingPredictor

load_dotenv()

# ---- Logging ----
os.makedirs("/app/logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/app/logs/api.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ---- Global predictor (loaded at startup) ----
predictor: Optional[HousingPredictor] = None


# ==================================================
# Pydantic request / response schemas
# ==================================================
class PredictionRequest(BaseModel):
    """Input features for a single prediction."""
    Bedrooms: int = Field(..., ge=1, le=10, description="Number of bedrooms")
    Bathrooms: int = Field(..., ge=1, le=5, description="Number of bathrooms")
    SquareFeet: float = Field(..., gt=0, description="Living area in sqft")
    Location: str = Field(
        ..., description="City name (New York, Los Angeles, Chicago, Houston)"
    )


class PredictionResponse(BaseModel):
    prediction: float
    model_version: str
    features_used: list


class TrainResponse(BaseModel):
    status: str
    metrics: dict
    timestamp: str
    model_path: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool


# ==================================================
# Lifespan — model is loaded here at startup
# ==================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the model at application startup."""
    global predictor

    logger.info("=" * 50)
    logger.info("FastAPI starting — loading model at startup...")
    logger.info("=" * 50)

    try:
        predictor = HousingPredictor()
        if predictor.is_loaded:
            logger.info("✅ Model loaded and ready for predictions")
        else:
            logger.warning("⚠️ No trained model found — /predict will return 503 until training is done")
    except Exception as e:
        logger.error(f"❌ Error during model loading: {e}")
        predictor = None

    yield  # App is running

    logger.info("FastAPI shutting down...")


# ==================================================
# FastAPI app
# ==================================================
app = FastAPI(
    title="Housing Price — Training & Inference API",
    description="Container 1: trains the model, serves predictions, exposes metrics.",
    version="1.0.0",
    lifespan=lifespan,
)


# ==================================================
# Endpoints
# ==================================================
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check — also reports whether a model is loaded."""
    return HealthResponse(
        status="healthy",
        model_loaded=predictor is not None and predictor.is_loaded,
    )


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Make a price prediction.
    
    The Django frontend calls this endpoint when a user submits features.
    """
    if predictor is None or not predictor.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please train a model first via POST /train",
        )

    try:
        features = {
            "Bedrooms": request.Bedrooms,
            "Bathrooms": request.Bathrooms,
            "SquareFeet": request.SquareFeet,
            "Location": request.Location,
        }
        result = predictor.predict(features)
        return PredictionResponse(**result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/train", response_model=TrainResponse)
async def trigger_training():
    """
    Trigger model retraining.
    
    After training, the model is reloaded automatically so the
    /predict endpoint serves the new version without a restart.
    """
    global predictor

    try:
        from src.train import train_model

        logger.info("Training triggered via API...")
        result = train_model()

        # Reload model after training
        if predictor is None:
            predictor = HousingPredictor()
        else:
            predictor.reload()

        logger.info("Model reloaded after training")

        return TrainResponse(
            status=result["status"],
            metrics=result["metrics"],
            timestamp=result["timestamp"],
            model_path=result["model_path"],
        )

    except Exception as e:
        logger.error(f"Training error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def get_metrics():
    """Return current model metrics and version info."""
    if predictor is None or not predictor.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded — no metrics available",
        )

    return {
        "metrics": predictor.feature_info["metrics"],
        "timestamp": predictor.feature_info["timestamp"],
        "model_params": predictor.feature_info.get("model_params", {}),
        "features": predictor.feature_info["feature_names"],
    }
