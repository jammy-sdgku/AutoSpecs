from django import forms

YEAR_CHOICES = [(str(y), str(y)) for y in range(2026, 1979, -1)]

class YMMSearchForm(forms.Form):
    year = forms.ChoiceField(
        choices=[('', 'Select Year')] + YEAR_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    make = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. Toyota'
        })
    )
    model = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. Camry'
        })
    )
    trim = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. XLE (optional)'
        })
    )


class VINSearchForm(forms.Form):
    vin = forms.CharField(
        min_length=17,
        max_length=17,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter 17-character VIN',
            'style': 'text-transform: uppercase;'
        })
    )

    def clean_vin(self):
        return self.cleaned_data['vin'].upper()