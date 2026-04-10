from decimal import Decimal, ROUND_HALF_UP

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class ParkingLot(models.Model):
    VEHICLE_TYPES = [
        ("car", "Car"),
        ("bike", "Bike / Motorcycle"),
        ("ev", "Electric Vehicle"),
    ]

    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=0)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=0)
    total_slots = models.PositiveIntegerField()
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_per_hour = models.DecimalField(max_digits=6, decimal_places=2)
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPES, default="car")
    image = models.ImageField(upload_to="parking_lots/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def available_slots(self):
        return self.slots.filter(
            is_available=True,
            occupancy_status__in=["empty", "unknown"],
        ).count()

    def occupied_slots(self):
        return self.slots.filter(occupancy_status="occupied").count()

    def __str__(self):
        return f"{self.name} - {self.city}"


class ParkingSlot(models.Model):
    VEHICLE_TYPES = [
        ("car", "Car"),
        ("bike", "Bike / Scooter"),
        ("ev", "Electric Vehicle"),
    ]

    OCCUPANCY_CHOICES = [
        ("empty", "Empty"),
        ("occupied", "Occupied"),
        ("unknown", "Unknown"),
    ]

    lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE, related_name="slots")
    slot_number = models.CharField(max_length=10)
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPES, default="car")
    is_available = models.BooleanField(default=True)

    # Hardware integration fields
    sensor_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    controller_id = models.CharField(max_length=50, blank=True)
    occupancy_status = models.CharField(
        max_length=10,
        choices=OCCUPANCY_CHOICES,
        default="empty",
    )
    last_sensor_update = models.DateTimeField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["lot", "slot_number"],
                name="unique_slot_number_per_lot",
            )
        ]
        ordering = ["lot_id", "slot_number"]

    def is_physically_empty(self):
        return self.occupancy_status in ["empty", "unknown"]

    def can_be_booked(self):
        return self.is_available and self.is_physically_empty()

    def mark_sensor_status(self, occupied, seen_at=None):
        self.occupancy_status = "occupied" if occupied else "empty"
        self.last_sensor_update = seen_at or timezone.now()
        self.save(update_fields=["occupancy_status", "last_sensor_update"])

    def __str__(self):
        return f"Slot {self.slot_number} ({self.vehicle_type}) - {self.lot.name}"


class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ("car", "Car"),
        ("bike", "Bike / Motorcycle"),
        ("ev", "Electric Vehicle"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vehicles")
    license_plate = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPES)
    model_name = models.CharField(max_length=100, blank=True)

    def save(self, *args, **kwargs):
        self.license_plate = self.license_plate.strip().upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.license_plate} ({self.user.username})"


class Booking(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("active", "Active"),
        ("completed", "Completed"),
        ("overstay", "Overstay - Fine Applied"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    slot = models.ForeignKey(ParkingSlot, on_delete=models.CASCADE, related_name="bookings")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="confirmed")
    total_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    fine_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        errors = {}

        if self.start_time and self.end_time:
            if self.status == "cancelled":
                if self.end_time < self.start_time:
                    errors["end_time"] = "End time cannot be before start time."
            elif self.end_time <= self.start_time:
                errors["end_time"] = "End time must be after start time."

        if self.vehicle_id and self.user_id and self.vehicle.user_id != self.user_id:
            errors["vehicle"] = "Selected vehicle does not belong to this user."

        if errors:
            raise ValidationError(errors)

    @property
    def total_payable(self):
        return (self.total_cost + self.fine_amount).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

    def save(self, *args, **kwargs):
        self.full_clean()

        if self.start_time and self.end_time and self.slot_id:
            duration_seconds = max((self.end_time - self.start_time).total_seconds(), 0)
            duration_hours = Decimal(str(duration_seconds)) / Decimal("3600")
            self.total_cost = (duration_hours * self.slot.lot.price_per_hour).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP,
            )

        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.end_time and self.status in ["confirmed", "active"]

    def is_active_now(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time and self.status in ["confirmed", "active"]

    def overstay_hours(self):
        if timezone.now() > self.end_time and self.status in ["confirmed", "active", "overstay"]:
            diff = timezone.now() - self.end_time
            return round(diff.total_seconds() / 3600, 1)
        return 0

    def __str__(self):
        return f"Booking #{self.id} by {self.user.username}"
