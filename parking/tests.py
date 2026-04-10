from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import BookingForm
from .models import Booking, ParkingLot, ParkingSlot, Vehicle


class BookingFormTests(TestCase):
    def test_end_time_must_be_after_start_time(self):
        start = timezone.now() + timedelta(hours=2)
        end = start - timedelta(minutes=30)

        form = BookingForm(
            data={
                "start_time": start.strftime("%Y-%m-%dT%H:%M"),
                "end_time": end.strftime("%Y-%m-%dT%H:%M"),
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("end_time", form.errors)

    def test_plate_requires_vehicle_type(self):
        start = timezone.now() + timedelta(hours=1)
        end = start + timedelta(hours=2)

        form = BookingForm(
            data={
                "start_time": start.strftime("%Y-%m-%dT%H:%M"),
                "end_time": end.strftime("%Y-%m-%dT%H:%M"),
                "license_plate": "KA01AB1234",
                "vehicle_type_choice": "",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("vehicle_type_choice", form.errors)


class BookingAndAuthViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="testpass123")
        self.other_user = User.objects.create_user(username="bob", password="testpass123")

        self.lot = ParkingLot.objects.create(
            name="Central Lot",
            address="MG Road",
            city="Bengaluru",
            latitude=12.9716,
            longitude=77.5946,
            total_slots=10,
            price_per_hour="50.00",
            vehicle_type="car",
            is_active=True,
        )

        self.slot = ParkingSlot.objects.create(
            lot=self.lot,
            slot_number="A1",
            vehicle_type="car",
            is_available=True,
        )

    def _create_booking(self, status="confirmed"):
        start = timezone.now() - timedelta(hours=1)
        end = timezone.now() + timedelta(hours=1)
        return Booking.objects.create(
            user=self.user,
            slot=self.slot,
            start_time=start,
            end_time=end,
            status=status,
        )

    def test_booking_cannot_attach_another_users_vehicle(self):
        Vehicle.objects.create(
            user=self.other_user,
            license_plate="KA01AB1234",
            vehicle_type="car",
            model_name="Other User Car",
        )

        self.client.force_login(self.user)

        start = timezone.now() + timedelta(hours=1)
        end = start + timedelta(hours=2)

        response = self.client.post(
            reverse("book_slot", args=[self.slot.id]),
            data={
                "start_time": start.strftime("%Y-%m-%dT%H:%M"),
                "end_time": end.strftime("%Y-%m-%dT%H:%M"),
                "license_plate": "KA01AB1234",
                "vehicle_type_choice": "car",
                "model_name": "My Car",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already registered to another user")
        self.assertEqual(Booking.objects.count(), 0)

    def test_cancel_booking_requires_post(self):
        booking = self._create_booking()
        self.client.force_login(self.user)

        response = self.client.get(reverse("cancel_booking", args=[booking.id]))
        self.assertEqual(response.status_code, 405)

    def test_extend_booking_rejects_negative_minutes(self):
        booking = self._create_booking(status="active")
        original_end_time = booking.end_time
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("extend_booking", args=[booking.id]),
            data={"extend_minutes": "-30"},
            follow=True,
        )

        booking.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(booking.end_time, original_end_time)

    def test_login_redirect_blocks_external_next_url(self):
        response = self.client.post(
            f"{reverse('login')}?next=https://evil.example/phish",
            data={"username": "alice", "password": "testpass123"},
        )

        self.assertRedirects(response, reverse("home"), fetch_redirect_response=False)
