from django.contrib import admin

from .models import Booking, ParkingLot, ParkingSlot, Vehicle


class ParkingSlotInline(admin.TabularInline):
    model = ParkingSlot
    extra = 1
    fields = [
        "slot_number",
        "vehicle_type",
        "is_available",
        "sensor_id",
        "controller_id",
        "occupancy_status",
        "last_sensor_update",
    ]
    readonly_fields = ["last_sensor_update"]


@admin.register(ParkingLot)
class ParkingLotAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "city",
        "total_slots",
        "available_slots",
        "occupied_slots",
        "price_per_hour",
        "is_active",
    ]
    list_filter = ["city", "is_active", "vehicle_type"]
    search_fields = ["name", "city", "address"]
    inlines = [ParkingSlotInline]


@admin.register(ParkingSlot)
class ParkingSlotAdmin(admin.ModelAdmin):
    list_display = [
        "slot_number",
        "lot",
        "vehicle_type",
        "is_available",
        "occupancy_status",
        "sensor_id",
        "controller_id",
        "last_sensor_update",
    ]
    list_filter = [
        "vehicle_type",
        "is_available",
        "occupancy_status",
        "lot",
    ]
    search_fields = ["slot_number", "sensor_id", "controller_id", "lot__name"]
    readonly_fields = ["last_sensor_update"]


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "slot",
        "start_time",
        "end_time",
        "status",
        "total_cost",
        "fine_amount",
    ]
    list_filter = ["status", "slot__lot"]
    search_fields = ["user__username", "slot__slot_number", "slot__lot__name"]
    readonly_fields = ["total_cost", "created_at"]


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ["license_plate", "user", "vehicle_type", "model_name"]
    list_filter = ["vehicle_type"]
    search_fields = ["license_plate", "user__username", "model_name"]
