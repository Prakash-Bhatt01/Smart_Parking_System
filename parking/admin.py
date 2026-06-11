from django.contrib import admin
from .models import ParkingLot, ParkingSlot, Booking, Vehicle, SlotConflictNotification


class ParkingSlotInline(admin.TabularInline):
    model = ParkingSlot
    extra = 5
    fields = ['slot_number', 'vehicle_type', 'is_available']


@admin.register(ParkingLot)
class ParkingLotAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'total_slots', 'available_slots', 'price_per_hour', 'is_active']
    list_filter  = ['city', 'is_active']
    search_fields = ['name', 'city']
    inlines = [ParkingSlotInline]


@admin.register(ParkingSlot)
class ParkingSlotAdmin(admin.ModelAdmin):
    list_display  = ['slot_number', 'vehicle_type', 'lot', 'is_available']
    list_filter   = ['vehicle_type', 'is_available', 'lot']
    search_fields = ['slot_number']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display  = ['id', 'user', 'slot', 'start_time', 'end_time', 'status', 'total_cost']
    list_filter   = ['status']
    search_fields = ['user__username']
    readonly_fields = ['total_cost', 'created_at']


@admin.register(SlotConflictNotification)
class SlotConflictNotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'slot', 'is_read', 'created_at']
    list_filter = ['is_read']
    search_fields = ['user__username', 'slot__slot_number']
    readonly_fields = ['created_at']

