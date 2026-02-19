"""
views.py - Django views for the predictor app.

Provides:
  - predict_view  — prediction form + API call
  - dashboard_view — live model metrics from /metrics endpoint
  - api_docs_view  — API endpoint documentation
  - health_view    — JSON health check
"""

import logging
import requests
from django.shortcuts import render
from django.conf import settings
from .forms import HousingPredictionForm

logger = logging.getLogger(__name__)

API_URL = settings.TRAINING_API_URL


# ==================================================================
# Helper: probe API health for sidebar status dot
# ==================================================================
def _get_api_status():
    """Quick probe to determine if the training API is online."""
    try:
        resp = requests.get(f"{API_URL}/health", timeout=3)
        data = resp.json()
        return {
            "api_online": True,
            "model_loaded": data.get("model_loaded", False),
            "api_status_class": "online",
            "api_status_text": "Online",
            "api_url": API_URL,
        }
    except Exception:
        return {
            "api_online": False,
            "model_loaded": False,
            "api_status_class": "offline",
            "api_status_text": "Offline",
            "api_url": API_URL,
        }


# ==================================================================
# Predict View
# ==================================================================
def predict_view(request):
    """
    Main view: renders the prediction form and displays results.

    On POST, sends features to the Training Service /predict endpoint
    and shows the predicted price.
    """
    prediction = None
    model_version = None
    error = None
    submitted_features = None

    if request.method == "POST":
        form = HousingPredictionForm(request.POST)
        if form.is_valid():
            payload = {
                "Bedrooms": form.cleaned_data["bedrooms"],
                "Bathrooms": form.cleaned_data["bathrooms"],
                "SquareFeet": form.cleaned_data["sqft_living"],
                "Location": form.cleaned_data["location"],
            }

            submitted_features = form.cleaned_data

            api_url = f"{API_URL}/predict"
            logger.info(f"Calling prediction API: {api_url} with {payload}")

            try:
                response = requests.post(api_url, json=payload, timeout=30)
                response.raise_for_status()
                result = response.json()
                prediction = result["prediction"]
                model_version = result.get("model_version", "unknown")
                logger.info(f"Prediction received: ${prediction:,.2f}")
            except requests.exceptions.ConnectionError:
                error = (
                    "Cannot connect to the prediction service. "
                    "Make sure the training-service container is running."
                )
                logger.error(error)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 503:
                    error = (
                        "Model is not loaded yet. Please train the model first "
                        "by calling POST /train on the training service."
                    )
                else:
                    error = f"Prediction API error: {e.response.text}"
                logger.error(error)
            except Exception as e:
                error = f"Unexpected error: {str(e)}"
                logger.error(error, exc_info=True)
    else:
        form = HousingPredictionForm()

    ctx = {
        "form": form,
        "prediction": prediction,
        "model_version": model_version,
        "error": error,
        "submitted_features": submitted_features,
        "active_page": "predict",
    }
    ctx.update(_get_api_status())

    return render(request, "predictor/predict.html", ctx)


# ==================================================================
# Dashboard View
# ==================================================================
def dashboard_view(request):
    """
    Dashboard showing live model metrics, parameters, and system status.
    Fetches data from the training service /metrics endpoint.
    """
    r2 = mae = rmse = trained_at = None
    model_params = {}
    features = []

    status = _get_api_status()

    if status["api_online"]:
        try:
            resp = requests.get(f"{API_URL}/metrics", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                metrics = data.get("metrics", {})
                r2 = f"{metrics.get('r2', 0):.4f}"
                mae = f"{metrics.get('mae', 0):,.2f}"
                rmse = f"{metrics.get('rmse', 0):,.2f}"
                trained_at = data.get("timestamp", "—")
                model_params = data.get("model_params", {})
                features = data.get("features", [])
        except Exception as e:
            logger.warning(f"Could not fetch metrics: {e}")

    ctx = {
        "active_page": "dashboard",
        "r2": r2,
        "mae": mae,
        "rmse": rmse,
        "trained_at": trained_at,
        "model_params": model_params,
        "features": features,
    }
    ctx.update(status)

    return render(request, "predictor/dashboard.html", ctx)


# ==================================================================
# API Docs View
# ==================================================================
def api_docs_view(request):
    """Static-ish page documenting the training service API endpoints."""
    ctx = {
        "active_page": "api_docs",
    }
    ctx.update(_get_api_status())
    return render(request, "predictor/api_docs.html", ctx)


# ==================================================================
# Health Check (JSON)
# ==================================================================
def health_view(request):
    """Simple health check endpoint for the Django app."""
    from django.http import JsonResponse

    training_status = "unknown"
    try:
        resp = requests.get(f"{API_URL}/health", timeout=5)
        training_status = resp.json()
    except Exception:
        training_status = "unreachable"

    return JsonResponse({
        "status": "healthy",
        "training_service": training_status,
    })
