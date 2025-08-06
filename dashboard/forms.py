from django import forms
from .models import Household, Appliance, ElectricityBill
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# forms.py
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import datetime

User = get_user_model()

class EmailUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ("username","email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already in use.")
        return email

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email')

class HouseholdForm(forms.ModelForm):
    class Meta:
        model = Household
        fields = ['members', 'rooms']

class ApplianceForm(forms.ModelForm):
    class Meta:
        model = Appliance
        fields = ['appliance_type', 'wattage', 'hours_used', 'custom_name']
        widgets = {
            'appliance_type': forms.Select(attrs={'class': 'form-select'}),
            'wattage': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'hours_used': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '24'}),
            'custom_name': forms.TextInput(attrs={'class': 'form-control'})
        }

class BillForm(forms.ModelForm):
    class Meta:
        model = ElectricityBill
        fields = ['amount', 'month', 'units_consumed']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'month': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),  # Changed to 'date' from 'month'
            'units_consumed': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make units_consumed optional in the form
        self.fields['units_consumed'].required = False
        self.fields['units_consumed'].help_text = 'Leave blank to calculate from bill amount'
        
        # Set initial date to first day of current month
        if not kwargs.get('instance'):
            today = datetime.date.today()
            self.fields['month'].initial = today.replace(day=1)
            
    def clean_month(self):
        """
        Custom validation to ensure the month field is handled correctly
        """
        month = self.cleaned_data.get('month')
        
        # If it's already a valid date, return it
        if isinstance(month, datetime.date):
            return month
            
        # Try to convert string formats
        try:
            # For HTML5 date input (YYYY-MM-DD)
            if isinstance(month, str) and '-' in month:
                return datetime.datetime.strptime(month, '%Y-%m-%d').date()
        except ValueError:
            pass
            
        # If conversion failed, raise validation error
        raise ValidationError("Enter a valid date in YYYY-MM-DD format.")