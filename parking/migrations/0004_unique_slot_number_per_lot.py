from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("parking", "0003_booking_fine_amount_parkinglot_fine_amount_and_more"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="parkingslot",
            constraint=models.UniqueConstraint(
                fields=("lot", "slot_number"),
                name="unique_slot_number_per_lot",
            ),
        ),
    ]
