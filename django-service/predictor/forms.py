"""
forms.py - Django form for housing price prediction input.

Provides a clean form with proper validation and widget attrs
that match the dark-themed UI system.
"""

from django import forms

LOCATION_CHOICES = [
    ("", "Select a city..."),
    ("New York", "New York"),
    ("Los Angeles", "Los Angeles"),
    ("Chicago", "Chicago"),
    ("Houston", "Houston"),
]


class HousingPredictionForm(forms.Form):
    """Form that collects housing features for price prediction."""

    bedrooms = forms.IntegerField(
        min_value=1,
        max_value=10,
        label="Bedrooms",
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "e.g. 3",
            "autocomplete": "off",
        }),
        error_messages={
            "min_value": "Must be at least 1 bedroom.",
            "max_value": "Maximum 10 bedrooms.",
            "required": "Please enter the number of bedrooms.",
        },
    )
    bathrooms = forms.IntegerField(
        min_value=1,
        max_value=5,
        label="Bathrooms",
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "e.g. 2",
            "autocomplete": "off",
        }),
        error_messages={
            "min_value": "Must be at least 1 bathroom.",
            "max_value": "Maximum 5 bathrooms.",
            "required": "Please enter the number of bathrooms.",
        },
    )
    sqft_living = forms.FloatField(
        min_value=100,
        max_value=10000,
        label="Living Area (sqft)",
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "e.g. 1800",
            "step": "1",
            "autocomplete": "off",
        }),
        error_messages={
            "min_value": "Minimum 100 sqft.",
            "max_value": "Maximum 10,000 sqft.",
            "required": "Please enter the living area.",
        },
    )
    location = forms.ChoiceField(
        choices=LOCATION_CHOICES,
        label="Location",
        widget=forms.Select(attrs={
            "class": "form-control",
        }),
        error_messages={
            "required": "Please select a location.",
            "invalid_choice": "Invalid city selection.",
        },
    )
