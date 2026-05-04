import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_parking.settings')
django.setup()

from parking.models import Booking, ParkingSlot, User
from django.utils import timezone
from datetime import timedelta

user = User.objects.get(username='testuser')
slot = ParkingSlot.objects.filter(is_available=True).first()

if slot:
    start = timezone.now() + timedelta(hours=1)
    end = start + timedelta(hours=2)
    booking = Booking.objects.create(
        user=user,
        slot=slot,
        start_time=start,
        end_time=end,
        total_cost=200,
        status='pending'
    )
    slot.is_available = False
    slot.save()
    print(f'Created booking ID: {booking.id}')
else:
    # Make a slot available
    slot = ParkingSlot.objects.first()
    slot.is_available = True
    slot.save()
    print(f'Made slot {slot.slot_number} available, please run again')
