#!/usr/bin/env python
"""
Script to fix duplicate slot numbers in the database before applying unique constraint
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_parking.settings')
django.setup()

from parking.models import ParkingSlot

# Find and fix duplicate slot numbers
duplicates = []
seen = set()

for slot in ParkingSlot.objects.all().order_by('lot_id', 'slot_number', 'id'):
    key = (slot.lot_id, slot.slot_number)
    if key in seen:
        duplicates.append(slot)
    else:
        seen.add(key)

print(f"Found {len(duplicates)} duplicate slots")

# Delete duplicate slots (keep the first one, delete the rest)
for slot in duplicates:
    print(f"Deleting duplicate slot: Lot {slot.lot_id}, Slot {slot.slot_number}, ID {slot.id}")
    slot.delete()

print("Duplicate slots removed successfully!")
