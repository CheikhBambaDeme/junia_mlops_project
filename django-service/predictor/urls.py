"""
URL configuration for the predictor app.
"""

from django.urls import path
from . import views

urlpatterns = [
    path("", views.predict_view, name="predict"),
    path("health/", views.health_view, name="health"),
]
