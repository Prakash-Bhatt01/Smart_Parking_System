# Implementation Plan: Demo Payment Flow

## Overview

This implementation plan breaks down the demo payment flow feature into discrete coding tasks. The feature adds a simulated payment step between booking creation and confirmation, transforming the current single-step booking process into a three-stage workflow: booking creation → payment processing → confirmation.

The implementation follows a phased approach: model changes and migrations first, then view modifications, URL routing, templates, and finally testing and validation.

## Tasks

- [x] 1. Update Booking model and create database migration
  - Modify the `Booking` model in `parking/models.py` to change the default status from 'confirmed' to 'pending'
  - Run `python manage.py makemigrations parking` to generate the migration file
  - Run `python manage.py migrate parking` to apply the migration
  - Verify that new bookings default to 'pending' status
  - _Requirements: 1.1, 1.2, 1.3, 6.1, 6.2, 6.3, 6.4_

- [x] 2. Modify book_slot view to redirect to payment page
  - Update the `book_slot` view in `parking/views.py` to remove the explicit `status='confirmed'` assignment
  - Change the redirect from `'my_bookings'` to `'payment_page'` with `booking_id` parameter
  - Keep the `slot.is_available = False` logic to reserve the slot immediately
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 7.1_

- [x] 3. Implement payment_page view
  - [x] 3.1 Create the payment_page view function in `parking/views.py`
    - Add `@login_required` decorator
    - Retrieve booking by ID and verify ownership with `user=request.user`
    - Check if booking status is 'pending', redirect to success page if already confirmed
    - Calculate duration in hours for display
    - Render `payment.html` template with booking context
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 9.1, 9.4_

  - [x]* 3.2 Write unit tests for payment_page view
    - Test that payment page displays booking details correctly
    - Test that accessing payment page with confirmed booking redirects to success page
    - Test that unauthorized users receive 404 error
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 4. Implement process_payment view
  - [x] 4.1 Create the process_payment view function in `parking/views.py`
    - Add `@login_required` decorator
    - Accept POST requests only, redirect to payment_page for GET requests
    - Retrieve booking by ID and verify ownership
    - Update booking status from 'pending' to 'confirmed'
    - Add success message using Django messages framework
    - Redirect to `booking_success` page with booking_id
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 9.2, 9.4_

  - [x]* 4.2 Write unit tests for process_payment view
    - Test that POST request updates booking status to 'confirmed'
    - Test that GET request redirects to payment page
    - Test that unauthorized users receive 404 error
    - Test that successful payment redirects to success page
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 5. Implement booking_success view
  - [x] 5.1 Create the booking_success view function in `parking/views.py`
    - Add `@login_required` decorator
    - Retrieve booking by ID and verify ownership
    - Calculate duration in hours for display
    - Render `booking_success.html` template with booking context
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 9.3, 9.4_

  - [x]* 5.2 Write unit tests for booking_success view
    - Test that success page displays booking confirmation details
    - Test that unauthorized users receive 404 error
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 6. Add URL routing for payment flow
  - Update `parking/urls.py` to add three new URL patterns:
    - `path('payment/<int:booking_id>/', views.payment_page, name='payment_page')`
    - `path('process-payment/<int:booking_id>/', views.process_payment, name='process_payment')`
    - `path('booking-success/<int:booking_id>/', views.booking_success, name='booking_success')`
  - _Requirements: 9.1, 9.2, 9.3, 9.4_

- [x] 7. Checkpoint - Verify backend implementation
  - Ensure all migrations are applied successfully
  - Ensure all new views are accessible via URL routing
  - Test creating a booking and verify redirect to payment page
  - Ask the user if questions arise

- [x] 8. Create payment.html template
  - [x] 8.1 Create the payment form template
    - Create `templates/payment.html` extending `base.html`
    - Implement split-screen layout with left branding panel and right form panel
    - Add booking summary section displaying slot number, location, duration, and total cost
    - Add payment form with fields: card number, cardholder name, expiry date, CVV
    - Add HTML5 validation patterns for all form fields
    - Add submit button labeled "Complete Payment"
    - Add demo payment disclaimer note
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.6, 8.1, 8.2, 8.3, 8.4, 8.5_

  - [x] 8.2 Add CSS styles for payment page
    - Add `.booking-summary` styles to `static/css/style.css`
    - Add `.summary-row` and `.summary-row.highlight` styles
    - Add `.payment-note` styles
    - Ensure responsive design for mobile devices
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.6_

- [x] 9. Create booking_success.html template
  - [x] 9.1 Create the success confirmation template
    - Create `templates/booking_success.html` extending `base.html`
    - Add success icon and confirmation message
    - Add booking details card displaying all booking information
    - Add navigation buttons to "My Bookings" and "Home" pages
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [x] 9.2 Add CSS styles for success page
    - Add `.success-page`, `.success-card`, `.success-icon` styles to `static/css/style.css`
    - Add `.booking-details-card`, `.detail-row` styles
    - Add `.success-actions` styles for button layout
    - Ensure responsive design for mobile devices
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 10. Checkpoint - Verify frontend implementation
  - Test payment form displays correctly with booking details
  - Test form validation for invalid card numbers, expiry dates, and CVV
  - Test payment submission and redirect to success page
  - Test success page displays all booking details correctly
  - Test navigation buttons on success page
  - Ask the user if questions arise

- [x]* 11. Write integration tests for complete payment flow
  - Test complete flow: create booking → payment page → submit payment → success page
  - Test that booking status changes from 'pending' to 'confirmed'
  - Test that slot remains unavailable after payment
  - Test idempotent payment confirmation (accessing payment page after confirmation)
  - _Requirements: 2.1, 2.2, 2.3, 4.1, 4.2, 4.3, 4.4, 5.1, 7.1, 7.2_

- [x]* 12. Write unit tests for booking model default status
  - Test that new Booking instances default to 'pending' status
  - Test that existing bookings retain their status values after migration
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 13. Final verification and cleanup
  - Run all tests to ensure no regressions
  - Verify that existing booking functionality (my_bookings, cancel_booking, extend_booking) still works correctly
  - Test the complete user journey from login to booking confirmation
  - Ensure all error scenarios are handled gracefully (404s, unauthorized access)
  - _Requirements: All_

## Notes

- Tasks marked with `*` are optional testing tasks and can be skipped for faster MVP delivery
- Each task references specific requirements from the requirements document for traceability
- The implementation follows Django best practices with proper authentication, authorization, and error handling
- The payment form is a demo feature with no real payment processing or gateway integration
- HTML5 form validation provides client-side validation without requiring server-side payment data validation
- Checkpoints ensure incremental validation and provide opportunities for user feedback
