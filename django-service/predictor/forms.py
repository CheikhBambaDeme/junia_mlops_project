"""
forms.py - Django form for housing price prediction input.
"""

from django import forms

LOCATION_CHOICES = [
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
        label="Number of Bedrooms",
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "e.g. 3",
        }),
    )
    bathrooms = forms.IntegerField(
        min_value=1,
        max_value=5,
        label="Number of Bathrooms",
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "e.g. 2",
        }),
    )
    sqft_living = forms.FloatField(
        min_value=100,
        max_value=10000,
        label="Living Area (sqft)",
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "e.g. 1800",
        }),
    )
    location = forms.ChoiceField(
        choices=LOCATION_CHOICES,
        label="Location",
        widget=forms.Select(attrs={
            "class": "form-control",
        }),
    )
