from django import forms
from .models import Employee


class EmployeeForm(forms.ModelForm):

    class Meta:
        model = Employee

        fields = [
            'name',
            'email',
            'phone',
            'designation',
            'salary',
            'photo'
        ]

        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),

            'email': forms.EmailInput(
                attrs={'class': 'form-control'}
            ),

            'phone': forms.TextInput(
                attrs={'class': 'form-control'}
            ),

            'designation': forms.Select(
                attrs={'class': 'form-control'}
            ),

            'salary': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0.01'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['designation'].empty_label = 'Select Designation'

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if not email:
            raise forms.ValidationError(
                'Email is required.'
            )

        if '@' not in email:
            raise forms.ValidationError(
                'Enter a valid email address.'
            )

        return email

    def clean_salary(self):
        salary = self.cleaned_data.get('salary')

        if salary is None or salary <= 0:
            raise forms.ValidationError(
                'Salary must be greater than 0.'
            )

        return salary