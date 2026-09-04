from django import forms
from .models import Designation


class DesignationForm(forms.ModelForm):

    class Meta:
        model = Designation

        fields = ['name']

        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter designation'
                }
            ),
        }