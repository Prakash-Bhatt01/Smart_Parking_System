# Generated data migration for seeding initial parking lots and slots

from django.db import migrations


def seed_parking_data(apps, schema_editor):
    """
    Seed the database with initial parking lots and slots.
    This migration is idempotent - it won't create duplicates.
    """
    ParkingLot = apps.get_model('parking', 'ParkingLot')
    ParkingSlot = apps.get_model('parking', 'ParkingSlot')
    
    # Only seed if database is empty
    if ParkingLot.objects.exists():
        print("Parking lots already exist. Skipping data seeding.")
        return
    
    print("Seeding initial parking data...")
    
    # Define parking lots with their data
    parking_lots_data = [
        {
            'name': 'Phoenix Market City Parking',
            'address': 'Whitefield Main Road, Mahadevapura',
            'city': 'Bengaluru',
            'latitude': 12.9975,
            'longitude': 77.6974,
            'total_slots': 27,
            'price_per_hour': 40.00,
            'fine_amount': 100.00,
            'slots': {
                'car': 15,
                'bike': 8,
                'ev': 4
            }
        },
        {
            'name': 'Manipal Hospital Parking',
            'address': 'HAL Old Airport Road',
            'city': 'Bengaluru',
            'latitude': 12.9579,
            'longitude': 77.6497,
            'total_slots': 18,
            'price_per_hour': 30.00,
            'fine_amount': 80.00,
            'slots': {
                'car': 10,
                'bike': 6,
                'ev': 2
            }
        },
        {
            'name': 'Kempegowda Airport Parking',
            'address': 'KIAL Road, Devanahalli',
            'city': 'Bengaluru',
            'latitude': 13.1986,
            'longitude': 77.7066,
            'total_slots': 26,
            'price_per_hour': 60.00,
            'fine_amount': 150.00,
            'slots': {
                'car': 15,
                'bike': 7,
                'ev': 4
            }
        },
        {
            'name': 'MG Road Metro Station',
            'address': 'Mahatma Gandhi Road',
            'city': 'Bengaluru',
            'latitude': 12.9757,
            'longitude': 77.6079,
            'total_slots': 20,
            'price_per_hour': 25.00,
            'fine_amount': 75.00,
            'slots': {
                'car': 10,
                'bike': 8,
                'ev': 2
            }
        },
        {
            'name': 'UB City Mall Parking',
            'address': '24 Vittal Mallya Road',
            'city': 'Bengaluru',
            'latitude': 12.9726,
            'longitude': 77.5987,
            'total_slots': 22,
            'price_per_hour': 50.00,
            'fine_amount': 120.00,
            'slots': {
                'car': 12,
                'bike': 7,
                'ev': 3
            }
        },
        {
            'name': 'Indiranagar 100 Feet Road',
            'address': '100 Feet Road, Indiranagar',
            'city': 'Bengaluru',
            'latitude': 12.9784,
            'longitude': 77.6408,
            'total_slots': 16,
            'price_per_hour': 35.00,
            'fine_amount': 90.00,
            'slots': {
                'car': 8,
                'bike': 6,
                'ev': 2
            }
        },
        {
            'name': 'Koramangala Forum Mall',
            'address': 'Koramangala 7th Block',
            'city': 'Bengaluru',
            'latitude': 12.9345,
            'longitude': 77.6101,
            'total_slots': 24,
            'price_per_hour': 45.00,
            'fine_amount': 110.00,
            'slots': {
                'car': 14,
                'bike': 7,
                'ev': 3
            }
        },
        {
            'name': 'Yeshwantpur Metro Station',
            'address': 'Yeshwantpur Circle',
            'city': 'Bengaluru',
            'latitude': 13.0286,
            'longitude': 77.5391,
            'total_slots': 18,
            'price_per_hour': 20.00,
            'fine_amount': 60.00,
            'slots': {
                'car': 10,
                'bike': 6,
                'ev': 2
            }
        },
    ]
    
    # Create parking lots and their slots
    created_lots = 0
    created_slots = 0
    
    for lot_data in parking_lots_data:
        # Extract slot configuration
        slots_config = lot_data.pop('slots')
        
        # Create parking lot
        lot = ParkingLot.objects.create(
            name=lot_data['name'],
            address=lot_data['address'],
            city=lot_data['city'],
            latitude=lot_data['latitude'],
            longitude=lot_data['longitude'],
            total_slots=lot_data['total_slots'],
            price_per_hour=lot_data['price_per_hour'],
            fine_amount=lot_data['fine_amount'],
            is_active=True
        )
        created_lots += 1
        
        # Create slots for each vehicle type
        slot_counter = 1
        
        # Create car slots
        for i in range(slots_config['car']):
            ParkingSlot.objects.create(
                lot=lot,
                slot_number=f'C{slot_counter:02d}',
                vehicle_type='car',
                is_available=True
            )
            slot_counter += 1
            created_slots += 1
        
        # Create bike slots
        slot_counter = 1
        for i in range(slots_config['bike']):
            ParkingSlot.objects.create(
                lot=lot,
                slot_number=f'B{slot_counter:02d}',
                vehicle_type='bike',
                is_available=True
            )
            slot_counter += 1
            created_slots += 1
        
        # Create EV slots
        slot_counter = 1
        for i in range(slots_config['ev']):
            ParkingSlot.objects.create(
                lot=lot,
                slot_number=f'E{slot_counter:02d}',
                vehicle_type='ev',
                is_available=True
            )
            slot_counter += 1
            created_slots += 1
    
    print(f"✅ Successfully created {created_lots} parking lots with {created_slots} slots")


def reverse_seed(apps, schema_editor):
    """
    Remove seeded data if migration is reversed.
    Only removes lots created by this migration.
    """
    ParkingLot = apps.get_model('parking', 'ParkingLot')
    
    # Delete parking lots (slots will cascade delete)
    lot_names = [
        'Phoenix Market City Parking',
        'Manipal Hospital Parking',
        'Kempegowda Airport Parking',
        'MG Road Metro Station',
        'UB City Mall Parking',
        'Indiranagar 100 Feet Road',
        'Koramangala Forum Mall',
        'Yeshwantpur Metro Station',
    ]
    
    deleted_count = ParkingLot.objects.filter(name__in=lot_names).delete()[0]
    print(f"Removed {deleted_count} parking lots")


class Migration(migrations.Migration):

    dependencies = [
        ('parking', '0010_add_conflict_notification'),
    ]

    operations = [
        migrations.RunPython(seed_parking_data, reverse_code=reverse_seed),
    ]
