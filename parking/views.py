from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import BookingForm, RegisterForm
from .models import Booking, ParkingLot, ParkingSlot, Vehicle


def home(request):
    lots = ParkingLot.objects.filter(is_active=True)[:6]
    return render(request, "home.html", {"lots": lots})


@login_required
def search_parking(request):
    lots = ParkingLot.objects.filter(is_active=True)
    city = request.GET.get("city", "").strip()
    vehicle_type = request.GET.get("vehicle_type", "").strip()

    if city:
        lots = lots.filter(city__icontains=city)
    if vehicle_type:
        lots = lots.filter(slots__vehicle_type=vehicle_type).distinct()

    return render(request, "search.html", {"lots": lots})


@login_required
def lot_detail(request, lot_id):
    lot = get_object_or_404(ParkingLot.objects.prefetch_related("slots"), id=lot_id)
    car_slots = lot.slots.filter(vehicle_type="car")
    bike_slots = lot.slots.filter(vehicle_type="bike")
    ev_slots = lot.slots.filter(vehicle_type="ev")
    available_count = lot.slots.filter(is_available=True).count()
    booked_count = lot.slots.filter(is_available=False).count()

    return render(
        request,
        "lot_detail.html",
        {
            "lot": lot,
            "car_slots": car_slots,
            "bike_slots": bike_slots,
            "ev_slots": ev_slots,
            "available_count": available_count,
            "booked_count": booked_count,
        },
    )


@login_required
def book_slot(request, slot_id):
    slot = get_object_or_404(ParkingSlot.objects.select_related("lot"), id=slot_id)

    if request.method == "GET" and not slot.is_available:
        messages.error(request, "This slot is no longer available.")
        return redirect("lot_detail", lot_id=slot.lot_id)

    form = BookingForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        license_plate = form.cleaned_data.get("license_plate")
        vehicle_type = form.cleaned_data.get("vehicle_type_choice")
        model_name = form.cleaned_data.get("model_name", "").strip()

        existing_vehicle = None
        if license_plate:
            existing_vehicle = Vehicle.objects.filter(license_plate=license_plate).first()

            if existing_vehicle and existing_vehicle.user_id != request.user.id:
                form.add_error(
                    "license_plate",
                    "This license plate is already registered to another user.",
                )

            if existing_vehicle and existing_vehicle.user_id == request.user.id:
                if existing_vehicle.vehicle_type != slot.vehicle_type:
                    form.add_error(
                        "vehicle_type_choice",
                        f"This slot only supports {slot.get_vehicle_type_display().lower()} vehicles.",
                    )
                elif vehicle_type and existing_vehicle.vehicle_type != vehicle_type:
                    form.add_error(
                        "vehicle_type_choice",
                        "Selected vehicle type does not match your saved vehicle.",
                    )

            if not existing_vehicle and vehicle_type and vehicle_type != slot.vehicle_type:
                form.add_error(
                    "vehicle_type_choice",
                    f"This slot only supports {slot.get_vehicle_type_display().lower()} vehicles.",
                )

        if not form.errors:
            try:
                with transaction.atomic():
                    locked_slot = ParkingSlot.objects.select_for_update().select_related("lot").get(
                        id=slot_id
                    )

                    if not locked_slot.is_available:
                        messages.error(
                            request,
                            "Sorry, this slot was just booked by someone else.",
                        )
                        return redirect("lot_detail", lot_id=locked_slot.lot_id)

                    vehicle = None
                    if license_plate:
                        vehicle = Vehicle.objects.filter(
                            license_plate=license_plate,
                            user=request.user,
                        ).first()

                        if vehicle is None:
                            vehicle = Vehicle.objects.create(
                                user=request.user,
                                license_plate=license_plate,
                                vehicle_type=vehicle_type,
                                model_name=model_name,
                            )
                        elif model_name and vehicle.model_name != model_name:
                            vehicle.model_name = model_name
                            vehicle.save(update_fields=["model_name"])

                    booking = form.save(commit=False)
                    booking.user = request.user
                    booking.slot = locked_slot
                    booking.vehicle = vehicle
                    booking.status = "confirmed"
                    booking.save()

                    locked_slot.is_available = False
                    locked_slot.save(update_fields=["is_available"])

            except ValidationError as exc:
                form.add_error(
                    None,
                    exc.messages[0] if exc.messages else "Unable to create the booking.",
                )
            else:
                messages.success(
                    request,
                    f"Slot {slot.slot_number} booked successfully!",
                )
                return redirect("my_bookings")

    return render(request, "book_slot.html", {"slot": slot, "form": form})


@login_required
def my_bookings(request):
    now = timezone.now()

    tracked_bookings = Booking.objects.select_related("slot__lot", "vehicle").filter(
        user=request.user,
        status__in=["confirmed", "active", "overstay"],
    )

    for booking in tracked_bookings:
        if booking.end_time < now:
            overstay = (now - booking.end_time).total_seconds() / 3600
            if overstay > 0.5:
                fine = round(overstay * float(booking.slot.lot.price_per_hour) * 2, 2)
                booking.fine_amount = fine
                booking.status = "overstay"
                booking.save()
            else:
                booking.fine_amount = 0
                booking.status = "completed"
                if not booking.slot.is_available:
                    booking.slot.is_available = True
                    booking.slot.save(update_fields=["is_available"])
                booking.save()
        elif booking.status in ["confirmed", "active"]:
            expected_status = "active" if booking.start_time <= now else "confirmed"
            if booking.status != expected_status:
                booking.status = expected_status
                booking.save(update_fields=["status"])

    bookings = Booking.objects.select_related("slot__lot", "vehicle").filter(
        user=request.user
    ).order_by("-created_at")

    active_bookings = bookings.exclude(status__in=["cancelled", "completed", "overstay"])
    completed_bookings = bookings.filter(status="completed")
    overstay_bookings = bookings.filter(status="overstay")
    cancelled_bookings = bookings.filter(status="cancelled")

    return render(
        request,
        "my_bookings.html",
        {
            "active_bookings": active_bookings,
            "completed_bookings": completed_bookings,
            "overstay_bookings": overstay_bookings,
            "cancelled_bookings": cancelled_bookings,
            "now": now,
        },
    )


@login_required
@require_POST
def cancel_booking(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related("slot"),
        id=booking_id,
        user=request.user,
    )

    if booking.status not in ["confirmed", "pending", "active", "overstay"]:
        messages.info(request, "This booking cannot be cancelled.")
        return redirect("my_bookings")

    now = timezone.now()
    if now <= booking.start_time:
        booking.end_time = booking.start_time
    else:
        booking.end_time = now

    booking.status = "cancelled"
    booking.fine_amount = 0
    booking.save()

    if not booking.slot.is_available:
        booking.slot.is_available = True
        booking.slot.save(update_fields=["is_available"])

    messages.success(request, "Booking cancelled.")
    return redirect("my_bookings")


@login_required
@require_POST
def extend_booking(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related("slot"),
        id=booking_id,
        user=request.user,
    )

    if booking.status not in ["confirmed", "active", "overstay"]:
        messages.error(request, "This booking cannot be extended.")
        return redirect("my_bookings")

    try:
        mins = int(request.POST.get("extend_minutes", "30"))
    except ValueError:
        mins = 0

    if mins <= 0:
        messages.error(request, "Extension minutes must be a positive number.")
        return redirect("my_bookings")

    now = timezone.now()
    base_end_time = booking.end_time if booking.end_time > now else now
    booking.end_time = base_end_time + timedelta(minutes=mins)
    booking.fine_amount = 0
    booking.status = "active" if booking.start_time <= now else "confirmed"
    booking.save()

    messages.success(request, f"Booking extended by {mins} minutes.")
    return redirect("my_bookings")


def register_view(request):
    form = RegisterForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f"Welcome, {user.first_name}!")
        return redirect("home")

    return render(request, "register.html", {"form": form})


def login_view(request):
    next_url = request.POST.get("next") or request.GET.get("next") or ""
    safe_next = ""

    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        safe_next = next_url

    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username", "").strip(),
            password=request.POST.get("password", ""),
        )
        if user:
            login(request, user)
            return redirect(safe_next or "home")
        messages.error(request, "Invalid username or password.")

    return render(request, "login.html", {"next": safe_next})


def logout_view(request):
    logout(request)
    return redirect("home")
