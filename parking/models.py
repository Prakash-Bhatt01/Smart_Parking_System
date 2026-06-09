from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ParkingLot(models.Model):
    VEHICLE_TYPES = [
        ('car', 'Car'),
        ('bike', 'Bike / Motorcycle'),
        ('ev', 'Electric Vehicle'),
    ]
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=0)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=0)
    total_slots = models.PositiveIntegerField()
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_per_hour = models.DecimalField(max_digits=6, decimal_places=2)
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPES, default='car')
    image = models.ImageField(upload_to='parking_lots/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def available_slots(self):
        return self.slots.filter(is_available=True).count()

    def __str__(self):
        return f"{self.name} - {self.city}"


class ParkingSlot(models.Model):
    VEHICLE_TYPES = [
        ('car', 'Car'),
        ('bike', 'Bike / Scooter'),
        ('ev', 'Electric Vehicle'),
    ]
    OCCUPANCY_STATUS_CHOICES = [
        ('empty', 'Empty'),
        ('occupied', 'Occupied'),
        ('unknown', 'Unknown'),
    ]
    lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE, related_name='slots')
    slot_number = models.CharField(max_length=10)
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPES, default='car')
    is_available = models.BooleanField(default=True)
    controller_id = models.CharField(max_length=50, blank=True, default='')
    sensor_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    occupancy_status = models.CharField(max_length=10, choices=OCCUPANCY_STATUS_CHOICES, default='empty')
    last_sensor_update = models.DateTimeField(blank=True, null=True)
    is_hardware_slot = models.BooleanField(default=False)
    hardware_slot_id = models.CharField(max_length=10, blank=True, default='')

    class Meta:
        ordering = ['lot_id', 'slot_number']

    def __str__(self):
        return f"Slot {self.slot_number} ({self.vehicle_type}) - {self.lot.name}"


class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ('car', 'Car'),
        ('bike', 'Bike / Motorcycle'),
        ('ev', 'Electric Vehicle'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles')
    license_plate = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPES)
    model_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.license_plate} ({self.user.username})"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('confirmed', 'Confirmed'),
        ('active',    'Active'),
        ('completed', 'Completed'),
        ('overstay',  'Overstay — Fine Applied'),
        ('cancelled', 'Cancelled'),
    ]
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    slot        = models.ForeignKey(ParkingSlot, on_delete=models.CASCADE, related_name='bookings')
    vehicle     = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    start_time  = models.DateTimeField()
    end_time    = models.DateTimeField()
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_cost  = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    fine_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    qr_code     = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        duration_hours = (self.end_time - self.start_time).total_seconds() / 3600
        if duration_hours < 0:
            duration_hours = 0
        self.total_cost = round(duration_hours * float(self.slot.lot.price_per_hour), 2)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.end_time and self.status in ['confirmed', 'active']

    def is_active_now(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time and self.status in ['confirmed', 'active']

    def overstay_hours(self):
        if timezone.now() > self.end_time and self.status in ['confirmed', 'active', 'overstay']:
            diff = timezone.now() - self.end_time
            return round(diff.total_seconds() / 3600, 1)
        return 0

    def __str__(self):
        return f"Booking #{self.id} by {self.user.username}"