from django import forms
from .models import Capture


class CaptureForm(forms.ModelForm):

    class Meta:
        model = Capture

        fields = [
            "fisher",
            "species",
            "length_cm",
            "photo"
        ]

        widgets = {

            "fisher": forms.Select(attrs={
                "class": "form-control"
            }),

            "species": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "length_cm": forms.NumberInput(attrs={
                "class": "form-control"
            }),

        }