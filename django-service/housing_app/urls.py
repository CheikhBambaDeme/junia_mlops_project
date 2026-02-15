"""
URL configuration for housing_app project.
"""

from django.urls import path, include

urlpatterns = [
    path("", include("predictor.urls")),
]
