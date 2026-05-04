from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from datetime import timedelta
from .models import Booking, Vehicle


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name',
                  'email', 'password1', 'password2']


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['license_plate', 'vehicle_type', 'model_name']


class BookingForm(forms.ModelForm):
    license_plate = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. KA01AB1234'
        })
    )
    vehicle_type_choice = forms.ChoiceField(
        choices=[
            ('', 'Select Type'),
            ('car', 'Car'),
            ('bike', 'Bike / Motorcycle'),
            ('ev', 'Electric Vehicle'),
        ],
        required=False
    )
    model_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. Honda City'
        })
    )

    class Meta:
        model = Booking
        fields = ['start_time', 'end_time']
        widgets = {
            'start_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}
            ),
            'end_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}
            ),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set default values for datetime fields
        now = timezone.now()
        # Round to next hour
        start_default = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        end_default = start_default + timedelta(hours=2)
        
        # Convert to local timezone for display
        if timezone.is_aware(start_default):
            start_default = timezone.localtime(start_default)
        if timezone.is_aware(end_default):
            end_default = timezone.localtime(end_default)
        
        # Set initial values if not bound (new form)
        if not self.is_bound:
            self.fields['start_time'].initial = start_default.strftime('%Y-%m-%dT%H:%M')
            self.fields['end_time'].initial = end_default.strftime('%Y-%m-%dT%H:%M')