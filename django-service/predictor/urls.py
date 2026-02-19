"""
URL configuration for the predictor app.
"""

from django.urls import path
from . import views

urlpatterns = [
    path("", views.predict_view, name="predict"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("api-docs/", views.api_docs_view, name="api_docs"),
    path("health/", views.health_view, name="health"),
]
