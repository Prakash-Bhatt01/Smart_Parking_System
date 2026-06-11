from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.files.base import ContentFile
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from .models import ParkingLot, ParkingSlot, Booking, Vehicle, SlotConflictNotification
from .forms import RegisterForm, BookingForm, VehicleForm
from datetime import timedelta
from django.utils.dateparse import parse_datetime
import qrcode
from io import BytesIO
import json


@never_cache
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
    
    # Get active bookings for this lot
    now = timezone.now()
    active_bookings = Booking.objects.filter(
        slot__lot=lot,
        status__in=['confirmed', 'active'],
        end_time__gt=now
    ).select_related('user', 'slot')
    
    # Build slot_booking_info dictionary
    slot_booking_info = {}
    for booking in active_bookings:
        slot_booking_info[booking.slot.id] = {
            'end_time': booking.end_time.isoformat(),
            'user_first_name': booking.user.first_name or booking.user.username,
            'booking_id': booking.id,
            'time_extended_by': booking.time_extended_by
        }
    
    # Convert to JSON string
    slot_booking_info_json = json.dumps(slot_booking_info)
    now_iso = now.isoformat()
    
    return render(request, 'lot_detail.html', {
        'lot':             lot,
        'car_slots':       car_slots,
        'bike_slots':      bike_slots,
        'ev_slots':        ev_slots,
        'available_count': available_count,
        'booked_count':    booked_count,
        'slot_booking_info_json': slot_booking_info_json,
        'now_iso': now_iso,
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
def check_slot_conflict(request, slot_id):
    """Check if a time slot conflicts with existing bookings"""
    try:
        slot = get_object_or_404(ParkingSlot, id=slot_id)
        
        # Get start_time and end_time from GET parameters
        start_time_str = request.GET.get('start_time')
        end_time_str = request.GET.get('end_time')
        
        if not start_time_str or not end_time_str:
            return JsonResponse({
                'error': True,
                'message': 'Missing start_time or end_time parameters'
            })
        
        # Parse datetime strings
        requested_start = parse_datetime(start_time_str)
        requested_end = parse_datetime(end_time_str)
        
        if not requested_start or not requested_end:
            return JsonResponse({
                'error': True,
                'message': 'Invalid datetime format'
            })
        
        # Check for conflicting bookings
        conflicting_bookings = Booking.objects.filter(
            slot=slot,
            status__in=['confirmed', 'active'],
            start_time__lt=requested_end,
            end_time__gt=requested_start
        ).select_related('user').order_by('end_time')
        
        if conflicting_bookings.exists():
            conflict = conflicting_bookings.first()
            
            # Find alternative slots in same lot with same vehicle type
            alternative_slots = ParkingSlot.objects.filter(
                lot=slot.lot,
                vehicle_type=slot.vehicle_type,
                is_available=True
            ).exclude(
                bookings__status__in=['confirmed', 'active'],
                bookings__start_time__lt=requested_end,
                bookings__end_time__gt=requested_start
            ).distinct()[:3]
            
            alternatives = []
            for alt_slot in alternative_slots:
                alternatives.append({
                    'slot_id': alt_slot.id,
                    'slot_number': alt_slot.slot_number,
                    'vehicle_type': alt_slot.vehicle_type
                })
            
            # Suggest booking from when conflict ends
            suggested_start = conflict.end_time
            suggested_end = suggested_start + timedelta(hours=1)
            
            return JsonResponse({
                'conflict': True,
                'message': f'We apologize, but this slot has an active booking until {conflict.end_time.strftime("%I:%M %p")}. Please choose another time or slot.',
                'blocked_until': conflict.end_time.strftime("%I:%M %p"),
                'slot_extended': conflict.time_extended_by > 0,
                'alternative_slots': alternatives,
                'suggested_start_time': suggested_start.isoformat(),
                'suggested_end_time': suggested_end.isoformat()
            })
        else:
            return JsonResponse({
                'conflict': False,
                'message': 'Slot is available for your selected time.'
            })
            
    except Exception as e:
        return JsonResponse({
            'error': True,
            'message': f'An error occurred: {str(e)}'
        })


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
    
    # Get unread conflict notifications
    conflict_notifications = SlotConflictNotification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-created_at')
    
    unread_notification_count = conflict_notifications.count()

    return render(request, 'my_bookings.html', {
        'active_bookings':    active_bookings,
        'completed_bookings': completed_bookings,
        'overstay_bookings':  overstay_bookings,
        'cancelled_bookings': cancelled_bookings,
        'conflict_notifications': conflict_notifications,
        'unread_notification_count': unread_notification_count,
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
    
    # Only accept POST requests
    if request.method != 'POST':
        return redirect('my_bookings')
    
    # Check booking status is confirmed or active
    if booking.status not in ['confirmed', 'active']:
        messages.error(request, 'This booking cannot be extended.')
        return redirect('my_bookings')
    
    # Get extend_minutes from POST data
    try:
        extend_minutes = int(request.POST.get('extend_minutes', '30'))
    except ValueError:
        extend_minutes = 30
    
    # Validate extend_minutes is either 30 or 60 only
    if extend_minutes not in [30, 60]:
        messages.error(request, 'Invalid extension duration. Please choose 30 or 60 minutes.')
        return redirect('my_bookings')
    
    # Calculate new total extended
    new_total_extended = booking.time_extended_by + extend_minutes
    
    # Check if new total would exceed 60 minutes
    if new_total_extended > 60:
        remaining = 60 - booking.time_extended_by
        messages.error(
            request, 
            f'Cannot extend more than 1 hour total. You have already extended {booking.time_extended_by} minutes. '
            f'Maximum remaining extension is {remaining} minutes.'
        )
        return redirect('my_bookings')
    
    # Store original end_time before extension
    original_end_time = booking.end_time
    
    # Add extend_minutes to booking.end_time
    booking.end_time = booking.end_time + timedelta(minutes=extend_minutes)
    
    # Update booking.time_extended_by
    booking.time_extended_by = new_total_extended
    
    # Recalculate booking.total_cost
    duration_hours = (booking.end_time - booking.start_time).total_seconds() / 3600
    booking.total_cost = round(duration_hours * float(booking.slot.lot.price_per_hour), 2)
    
    # Save the booking
    booking.save()
    
    # Check for conflicting bookings after extension
    conflicting_bookings = Booking.objects.filter(
        slot=booking.slot,
        status__in=['confirmed', 'active'],
        start_time__lt=booking.end_time,
        end_time__gt=original_end_time
    ).exclude(id=booking.id)
    
    # Create notifications for conflicting bookings
    for conflicting_booking in conflicting_bookings:
        notification_message = (
            f"We apologize, but Slot {booking.slot.slot_number} at {booking.slot.lot.name} "
            f"has recently been extended until {booking.end_time.strftime('%I:%M %p on %B %d, %Y')} "
            f"by another user and is no longer available for your selected time period. "
            f"We suggest booking from {booking.end_time.strftime('%I:%M %p')} onwards or choosing an alternative available slot."
        )
        
        SlotConflictNotification.objects.create(
            user=conflicting_booking.user,
            slot=booking.slot,
            message=notification_message,
            suggested_start_time=booking.end_time,
            is_read=False
        )
    
    # Show success message
    new_end_time = booking.end_time.strftime('%I:%M %p')
    messages.success(
        request, 
        f'Parking time extended by {extend_minutes} minutes. New end time is {new_end_time}. Additional cost added.'
    )
    
    return redirect('my_bookings')


@login_required
def mark_notification_read(request, notification_id):
    """Mark a conflict notification as read"""
    notification = get_object_or_404(
        SlotConflictNotification, 
        id=notification_id,
        user=request.user
    )
    notification.is_read = True
    notification.save()
    return JsonResponse({"status": "ok"})


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