from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Booking, Vehicle

DATETIME_LOCAL_FORMAT = "%Y-%m-%dT%H:%M"


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"].strip()
        user.last_name = self.cleaned_data["last_name"].strip()
        if commit:
            user.save()
        return user


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ["license_plate", "vehicle_type", "model_name"]

    def clean_license_plate(self):
        plate = self.cleaned_data["license_plate"].strip().upper()
        existing = Vehicle.objects.filter(license_plate=plate).exclude(pk=self.instance.pk)
        if existing.exists():
            current_user_id = getattr(self.instance, "user_id", None)
            if existing.first().user_id != current_user_id:
                raise forms.ValidationError(
                    "This license plate is already registered to another user."
                )
        return plate


class BookingForm(forms.ModelForm):
    license_plate = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "e.g. KA01AB1234"}),
    )
    vehicle_type_choice = forms.ChoiceField(
        choices=[
            ("", "Select Type"),
            ("car", "Car"),
            ("bike", "Bike / Motorcycle"),
            ("ev", "Electric Vehicle"),
        ],
        required=False,
    )
    model_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "e.g. Honda City"}),
    )

    class Meta:
        model = Booking
        fields = ["start_time", "end_time"]
        widgets = {
            "start_time": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format=DATETIME_LOCAL_FORMAT,
            ),
            "end_time": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format=DATETIME_LOCAL_FORMAT,
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["start_time"].input_formats = [DATETIME_LOCAL_FORMAT]
        self.fields["end_time"].input_formats = [DATETIME_LOCAL_FORMAT]

    def clean_license_plate(self):
        plate = self.cleaned_data.get("license_plate", "").strip().upper()
        return plate

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        license_plate = cleaned_data.get("license_plate")
        vehicle_type = cleaned_data.get("vehicle_type_choice")
        model_name = cleaned_data.get("model_name", "").strip()

        if start_time and end_time and end_time <= start_time:
            self.add_error("end_time", "End time must be after start time.")

        if license_plate and not vehicle_type:
            self.add_error(
                "vehicle_type_choice",
                "Select the vehicle type for this license plate.",
            )

        if vehicle_type and not license_plate:
            self.add_error(
                "license_plate",
                "Enter the license plate number for this vehicle.",
            )

        if model_name and not license_plate:
            self.add_error(
                "license_plate",
                "Enter the license plate number before adding a model name.",
            )

        return cleaned_data
