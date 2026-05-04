from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta
from .models import ParkingLot, ParkingSlot, Vehicle, Booking


class BookingModelTestCase(TestCase):
    """Test cases for Booking model"""
    
    def setUp(self):
        """Set up test data"""
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create a parking lot
        self.lot = ParkingLot.objects.create(
            name='Test Parking Lot',
            address='123 Test St',
            city='Test City',
            total_slots=10,
            price_per_hour=50.00,
            vehicle_type='car'
        )
        
        # Create a parking slot
        self.slot = ParkingSlot.objects.create(
            lot=self.lot,
            slot_number='A1',
            vehicle_type='car',
            is_available=True
        )
        
        # Create a vehicle
        self.vehicle = Vehicle.objects.create(
            user=self.user,
            license_plate='TEST123',
            vehicle_type='car',
            model_name='Test Car'
        )
    
    def test_booking_default_status_is_pending(self):
        """Test that new bookings default to 'pending' status"""
        start_time = timezone.now() + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)
        
        # Create a booking without specifying status
        booking = Booking.objects.create(
            user=self.user,
            slot=self.slot,
            vehicle=self.vehicle,
            start_time=start_time,
            end_time=end_time
        )
        
        # Assert that the status is 'pending'
        self.assertEqual(booking.status, 'pending')
        
    def test_booking_can_be_created_with_explicit_status(self):
        """Test that bookings can still be created with explicit status"""
        start_time = timezone.now() + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)
        
        # Create a booking with explicit 'confirmed' status
        booking = Booking.objects.create(
            user=self.user,
            slot=self.slot,
            vehicle=self.vehicle,
            start_time=start_time,
            end_time=end_time,
            status='confirmed'
        )
        
        # Assert that the status is 'confirmed'
        self.assertEqual(booking.status, 'confirmed')


class PaymentFlowTestCase(TestCase):
    """Test cases for the complete payment flow"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create a test user
        self.user = User.objects.create_user(
            username='flowuser',
            password='testpass123',
            email='flow@example.com',
            first_name='Flow',
            last_name='User'
        )
        
        # Create a parking lot
        self.lot = ParkingLot.objects.create(
            name='Flow Parking Lot',
            address='456 Flow St',
            city='Flow City',
            total_slots=10,
            price_per_hour=50.00,
            vehicle_type='car',
            is_active=True
        )
        
        # Create a parking slot
        self.slot = ParkingSlot.objects.create(
            lot=self.lot,
            slot_number='B1',
            vehicle_type='car',
            is_available=True
        )
    
    def test_complete_booking_flow(self):
        """Test the complete flow: login -> book -> payment -> confirmation"""
        # Step 1: Login
        self.client.login(username='flowuser', password='testpass123')
        
        # Step 2: Book a slot
        start_time = timezone.now() + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)
        
        booking_data = {
            'start_time': start_time.strftime('%Y-%m-%dT%H:%M'),
            'end_time': end_time.strftime('%Y-%m-%dT%H:%M'),
            'license_plate': 'FLOW123',
            'vehicle_type_choice': 'car',
            'model_name': 'Flow Car'
        }
        
        response = self.client.post(f'/book/{self.slot.id}/', booking_data, follow=False)
        self.assertEqual(response.status_code, 302, "Booking submission should redirect")
        
        # Verify booking was created with pending status
        booking = Booking.objects.filter(user=self.user).first()
        self.assertIsNotNone(booking, "Booking should be created")
        self.assertEqual(booking.status, 'pending', "Booking status should be 'pending'")
        
        # Verify slot is marked unavailable
        self.slot.refresh_from_db()
        self.assertFalse(self.slot.is_available, "Slot should be marked unavailable")
        
        # Verify redirect to payment page
        self.assertIn(f'/payment/{booking.id}/', response.url, "Should redirect to payment page")
        
        # Step 3: Access payment page
        response = self.client.get(f'/payment/{booking.id}/')
        self.assertEqual(response.status_code, 200, "Payment page should load")
        self.assertContains(response, 'Complete Payment')
        self.assertContains(response, booking.slot.slot_number)
        
        # Step 4: Submit payment
        payment_data = {
            'card_number': '1234567890123456',
            'card_name': 'Flow User',
            'expiry': '12/25',
            'cvv': '123'
        }
        
        response = self.client.post(f'/process-payment/{booking.id}/', payment_data, follow=False)
        self.assertEqual(response.status_code, 302, "Payment processing should redirect")
        
        # Verify booking status updated to confirmed
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'confirmed', "Booking status should be 'confirmed'")
        
        # Verify redirect to success page
        self.assertIn(f'/booking-success/{booking.id}/', response.url, "Should redirect to success page")
        
        # Step 5: Access success page
        response = self.client.get(f'/booking-success/{booking.id}/')
        self.assertEqual(response.status_code, 200, "Success page should load")
        self.assertContains(response, 'Booking Confirmed')
        self.assertContains(response, booking.slot.slot_number)
    
    def test_existing_booking_functionality(self):
        """Test that existing booking functionality still works correctly"""
        self.client.login(username='flowuser', password='testpass123')
        
        # Create a confirmed booking
        start_time = timezone.now() + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)
        
        booking = Booking.objects.create(
            user=self.user,
            slot=self.slot,
            start_time=start_time,
            end_time=end_time,
            status='confirmed'
        )
        self.slot.is_available = False
        self.slot.save()
        
        # Test My Bookings page
        response = self.client.get('/my-bookings/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, booking.slot.slot_number)
        
        # Test Cancel Booking
        response = self.client.post(f'/cancel/{booking.id}/', follow=True)
        self.assertEqual(response.status_code, 200)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'cancelled')
        self.slot.refresh_from_db()
        self.assertTrue(self.slot.is_available, "Slot should be available after cancellation")
        
        # Test Extend Booking
        booking.status = 'active'
        booking.save()
        original_end_time = booking.end_time
        
        response = self.client.post(f'/extend/{booking.id}/', {'extend_minutes': '30'}, follow=True)
        self.assertEqual(response.status_code, 200)
        booking.refresh_from_db()
        self.assertGreater(booking.end_time, original_end_time, "End time should be extended")
    
    def test_error_scenarios(self):
        """Test error scenarios are handled gracefully"""
        self.client.login(username='flowuser', password='testpass123')
        
        # Test 1: Access payment page with invalid booking ID
        response = self.client.get('/payment/99999/')
        self.assertEqual(response.status_code, 404, "Should return 404 for invalid booking ID")
        
        # Test 2: Access another user's booking
        other_user = User.objects.create_user(username='otheruser', password='pass123')
        start_time = timezone.now() + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)
        
        other_booking = Booking.objects.create(
            user=other_user,
            slot=self.slot,
            start_time=start_time,
            end_time=end_time,
            status='pending'
        )
        
        response = self.client.get(f'/payment/{other_booking.id}/')
        self.assertEqual(response.status_code, 404, "Should return 404 for unauthorized access")
        
        # Test 3: Access payment page for already confirmed booking
        confirmed_booking = Booking.objects.create(
            user=self.user,
            slot=self.slot,
            start_time=start_time,
            end_time=end_time,
            status='confirmed'
        )
        
        response = self.client.get(f'/payment/{confirmed_booking.id}/', follow=False)
        self.assertEqual(response.status_code, 302, "Should redirect for confirmed booking")
        self.assertIn(f'/booking-success/{confirmed_booking.id}/', response.url)
        
        # Test 4: GET request to process_payment
        pending_booking = Booking.objects.create(
            user=self.user,
            slot=self.slot,
            start_time=start_time,
            end_time=end_time,
            status='pending'
        )
        
        response = self.client.get(f'/process-payment/{pending_booking.id}/', follow=False)
        self.assertEqual(response.status_code, 302, "Should redirect GET requests")
        self.assertIn(f'/payment/{pending_booking.id}/', response.url)
        
        # Test 5: Unauthenticated access
        self.client.logout()
        response = self.client.get(f'/payment/{pending_booking.id}/', follow=False)
        self.assertEqual(response.status_code, 302, "Should redirect unauthenticated users")
        self.assertIn('/login/', response.url)
