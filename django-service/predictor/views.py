"""
views.py - Django views for the predictor app.

When the user submits the form, this view calls the
Training Service API (Container 1) to get a prediction.
"""

import logging
import requests
from django.shortcuts import render
from django.conf import settings
from .forms import HousingPredictionForm

logger = logging.getLogger(__name__)


def predict_view(request):
    """
    Main view: renders the prediction form and displays results.
    
    On POST, sends features to the Training Service /predict endpoint
    and shows the predicted price.
    """
    prediction = None
    model_version = None
    error = None

    if request.method == "POST":
        form = HousingPredictionForm(request.POST)
        if form.is_valid():
            # Build the payload matching the FastAPI schema
            payload = {
                "Bedrooms": form.cleaned_data["bedrooms"],
                "Bathrooms": form.cleaned_data["bathrooms"],
                "SquareFeet": form.cleaned_data["sqft_living"],
                "Location": form.cleaned_data["location"],
            }

            api_url = f"{settings.TRAINING_API_URL}/predict"
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
                        "by calling POST http://localhost:8000/train"
                    )
                else:
                    error = f"Prediction API error: {e.response.text}"
                logger.error(error)
            except Exception as e:
                error = f"Unexpected error: {str(e)}"
                logger.error(error, exc_info=True)
    else:
        form = HousingPredictionForm()

    return render(
        request,
        "predictor/predict.html",
        {
            "form": form,
            "prediction": prediction,
            "model_version": model_version,
            "error": error,
        },
    )


def health_view(request):
    """Simple health check endpoint for the Django app."""
    from django.http import JsonResponse

    # Also check if training service is reachable
    training_status = "unknown"
    try:
        resp = requests.get(f"{settings.TRAINING_API_URL}/health", timeout=5)
        training_status = resp.json()
    except Exception:
        training_status = "unreachable"

    return JsonResponse({
        "status": "healthy",
        "training_service": training_status,
    })
