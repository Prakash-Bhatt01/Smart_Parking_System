from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.files.base import ContentFile
from .models import ParkingLot, ParkingSlot, Booking, Vehicle
from .forms import RegisterForm, BookingForm, VehicleForm
from datetime import timedelta
import qrcode
from io import BytesIO


def home(request):
    lots = ParkingLot.objects.filter(is_active=True)[:6]
    return render(request, 'home.html', {'lots': lots})


@login_required
def search_parking(request):
    lots = ParkingLot.objects.filter(is_active=True)
    city = request.GET.get('city', '')
    vehicle_type = request.GET.get('vehicle_type', '')
    if city:
        lots = lots.filter(city__icontains=city)
    if vehicle_type:
        lots = lots.filter(slots__vehicle_type=vehicle_type).distinct()
    return render(request, 'search.html', {'lots': lots})


@login_required
def lot_detail(request, lot_id):
    lot = get_object_or_404(ParkingLot, id=lot_id)
    car_slots       = lot.slots.filter(vehicle_type='car')
    bike_slots      = lot.slots.filter(vehicle_type='bike')
    ev_slots        = lot.slots.filter(vehicle_type='ev')
    available_count = lot.slots.filter(is_available=True).count()
    booked_count    = lot.slots.filter(is_available=False).count()
    return render(request, 'lot_detail.html', {
        'lot':             lot,
        'car_slots':       car_slots,
        'bike_slots':      bike_slots,
        'ev_slots':        ev_slots,
        'available_count': available_count,
        'booked_count':    booked_count,
    })


@login_required
def book_slot(request, slot_id):
    slot = get_object_or_404(ParkingSlot, id=slot_id, is_available=True)
    form = BookingForm()
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            license_plate = form.cleaned_data.get('license_plate')
            vehicle = None
            if license_plate:
                vehicle, created = Vehicle.objects.get_or_create(
                    license_plate=license_plate,
                    defaults={
                        'user': request.user,
                        'vehicle_type': form.cleaned_data.get('vehicle_type_choice') or 'car',
                        'model_name': form.cleaned_data.get('model_name', '')
                    }
                )
            booking = form.save(commit=False)
            booking.user    = request.user
            booking.slot    = slot
            booking.vehicle = vehicle
            booking.save()
            slot.is_available = False
            slot.save()
            messages.success(request, f'Slot {slot.slot_number} booked successfully!')
            return redirect('payment_page', booking_id=booking.id)
    return render(request, 'book_slot.html', {'slot': slot, 'form': form})


@login_required
def payment_page(request, booking_id):
    """Display payment form for a pending booking."""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # If already confirmed, redirect to success page (idempotent)
    if booking.status != 'pending':
        return redirect('booking_success', booking_id=booking.id)
    
    # Calculate duration for display
    duration = booking.end_time - booking.start_time
    duration_hours = duration.total_seconds() / 3600
    
    context = {
        'booking': booking,
        'duration_hours': round(duration_hours, 1),
    }
    return render(request, 'payment.html', context)


@login_required
def process_payment(request, booking_id):
    """Process payment submission and confirm booking."""
    # Accept POST requests only, redirect to payment_page for GET requests
    if request.method != 'POST':
        return redirect('payment_page', booking_id=booking_id)
    
    # Retrieve booking by ID and verify ownership
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Update booking status from 'pending' to 'confirmed'
    booking.status = 'confirmed'
    booking.save()
    
    # Generate QR code containing Booking ID and Slot Number
    qr_data = f"Booking ID: {booking.id}\nSlot: {booking.slot.slot_number}\nLot: {booking.slot.lot.name}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Create QR code image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to BytesIO buffer
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Save to booking's qr_code field
    booking.qr_code.save(f'booking_{booking.id}_qr.png', ContentFile(buffer.read()), save=True)
    
    # Add success message using Django messages framework
    messages.success(request, 'Payment successful! Your booking is confirmed.')
    
    # Redirect to booking_success page with booking_id
    return redirect('booking_success', booking_id=booking.id)


@login_required
def booking_success(request, booking_id):
    """Display booking confirmation after successful payment."""
    # Retrieve booking by ID and verify ownership
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Calculate duration in hours for display
    duration = booking.end_time - booking.start_time
    duration_hours = duration.total_seconds() / 3600
    
    context = {
        'booking': booking,
        'duration_hours': round(duration_hours, 1),
    }
    return render(request, 'booking_success.html', context)


@login_required
def my_bookings(request):
    now = timezone.now()

    # Auto-update expired bookings
    expired = Booking.objects.filter(
        user=request.user,
        status__in=['confirmed', 'active'],
        end_time__lt=now
    )
    for booking in expired:
        overstay = (now - booking.end_time).total_seconds() / 3600
        if overstay > 0.5:
            fine = round(overstay * float(booking.slot.lot.price_per_hour) * 2, 2)
            booking.fine_amount = fine
            booking.status = 'overstay'
        else:
            booking.status = 'completed'
            booking.slot.is_available = True
            booking.slot.save()
        booking.save()

    active_bookings = Booking.objects.filter(
        user=request.user
    ).exclude(
        status__in=['cancelled', 'completed', 'overstay']
    ).order_by('-created_at')

    completed_bookings = Booking.objects.filter(
        user=request.user,
        status='completed'
    ).order_by('-created_at')

    overstay_bookings = Booking.objects.filter(
        user=request.user,
        status='overstay'
    ).order_by('-created_at')

    cancelled_bookings = Booking.objects.filter(
        user=request.user,
        status='cancelled'
    ).order_by('-created_at')

    return render(request, 'my_bookings.html', {
        'active_bookings':    active_bookings,
        'completed_bookings': completed_bookings,
        'overstay_bookings':  overstay_bookings,
        'cancelled_bookings': cancelled_bookings,
        'now': now,
    })


@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.status in ['confirmed', 'pending', 'active', 'overstay']:
        # If the booking is currently active or overstaying, end it at cancellation time so cost is calculated correctly
        if booking.status in ['active', 'overstay']:
            booking.end_time = timezone.now()
        booking.status = 'cancelled'
        booking.save()
        booking.slot.is_available = True
        booking.slot.save()
        messages.success(request, 'Booking cancelled.')
    return redirect('my_bookings')


@login_required
def extend_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if request.method == 'POST' and booking.status in ['confirmed', 'active', 'overstay']:
        try:
            mins = int(request.POST.get('extend_minutes', '30'))
        except ValueError:
            mins = 30
        booking.end_time = booking.end_time + timedelta(minutes=mins)
        now = timezone.now()
        # If end_time is now in the future, clear overstay and recompute
        if booking.end_time > now:
            booking.fine_amount = 0
            booking.status = 'active' if booking.start_time <= now else 'confirmed'
        booking.save()
        messages.success(request, f'Booking extended by {mins} minutes.')
    return redirect('my_bookings')


def register_view(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name}!')
            return redirect('home')
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        user = authenticate(request,
                            username=request.POST['username'],
                            password=request.POST['password'])
        if user:
            login(request, user)
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
        return redirect('home')
    else:
        # Handle GET request - redirect to logout confirmation or just logout
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
        return redirect('home')


@login_required
def profile_view(request):
    """Display user profile with booking statistics"""
    user = request.user
    
    # Calculate booking statistics
    total_bookings = Booking.objects.filter(user=user).count()
    active_bookings = Booking.objects.filter(
        user=user,
        status__in=['pending', 'confirmed', 'active']
    ).count()
    completed_bookings = Booking.objects.filter(
        user=user,
        status='completed'
    ).count()
    cancelled_bookings = Booking.objects.filter(
        user=user,
        status='cancelled'
    ).count()
    
    # Get recent bookings for display
    recent_bookings = Booking.objects.filter(user=user).order_by('-created_at')[:5]
    
    context = {
        'user': user,
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'completed_bookings': completed_bookings,
        'cancelled_bookings': cancelled_bookings,
        'recent_bookings': recent_bookings,
    }
    
    return render(request, 'profile.html', context)