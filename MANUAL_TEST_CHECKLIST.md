# Manual Test Checklist for Payment Flow

This checklist can be used for manual visual verification of the payment flow feature.

## Prerequisites
- [ ] Development server is running (`python manage.py runserver`)
- [ ] Database has test data (parking lots, slots)
- [ ] Test user account exists

## Test Scenario 1: Complete Booking Flow

### Step 1: Login
- [ ] Navigate to http://localhost:8000/login/
- [ ] Enter credentials and log in
- [ ] Verify redirect to home page

### Step 2: Browse and Select Parking
- [ ] Browse available parking lots
- [ ] Click on a parking lot to view details
- [ ] Verify available slots are displayed
- [ ] Click "Book Now" on an available slot

### Step 3: Create Booking
- [ ] Fill in booking form:
  - [ ] Start time (future time)
  - [ ] End time (after start time)
  - [ ] License plate
  - [ ] Vehicle type
  - [ ] Model name
- [ ] Click "Book Slot"
- [ ] Verify redirect to payment page

### Step 4: Payment Page
- [ ] Verify left panel displays:
  - [ ] SmartPark logo
  - [ ] "Secure Payment" heading
  - [ ] Feature highlights with icons
- [ ] Verify right panel displays:
  - [ ] "Complete Payment" heading
  - [ ] Booking summary with:
    - [ ] Slot number
    - [ ] Location name
    - [ ] Duration in hours
    - [ ] Total cost
  - [ ] Payment form fields:
    - [ ] Card number (16 digits)
    - [ ] Cardholder name
    - [ ] Expiry date (MM/YY)
    - [ ] CVV (3-4 digits)
  - [ ] "Complete Payment" button
  - [ ] Demo payment disclaimer

### Step 5: Submit Payment
- [ ] Enter test payment details:
  - Card: 1234567890123456
  - Name: Test User
  - Expiry: 12/25
  - CVV: 123
- [ ] Click "Complete Payment"
- [ ] Verify redirect to success page

### Step 6: Success Page
- [ ] Verify success icon (green checkmark)
- [ ] Verify "Booking Confirmed!" heading
- [ ] Verify booking details card shows:
  - [ ] Booking ID
  - [ ] Slot number
  - [ ] Parking lot name
  - [ ] Address
  - [ ] Start time
  - [ ] End time
  - [ ] Duration
  - [ ] Total paid (highlighted)
- [ ] Verify action buttons:
  - [ ] "View My Bookings" button
  - [ ] "Back to Home" button

### Step 7: My Bookings
- [ ] Click "View My Bookings"
- [ ] Verify booking appears in active bookings
- [ ] Verify status shows "Confirmed"
- [ ] Verify booking details are correct

## Test Scenario 2: Form Validation

### Invalid Card Number
- [ ] Create a booking
- [ ] On payment page, enter invalid card number (e.g., "1234")
- [ ] Try to submit
- [ ] Verify browser validation error appears

### Invalid Expiry Date
- [ ] Enter invalid expiry format (e.g., "13/25" or "1/25")
- [ ] Try to submit
- [ ] Verify browser validation error appears

### Invalid CVV
- [ ] Enter invalid CVV (e.g., "12" or "abcd")
- [ ] Try to submit
- [ ] Verify browser validation error appears

### Empty Fields
- [ ] Leave fields empty
- [ ] Try to submit
- [ ] Verify required field validation appears

## Test Scenario 3: Error Handling

### Invalid Booking ID
- [ ] Manually navigate to `/payment/99999/`
- [ ] Verify 404 error page appears

### Already Confirmed Booking
- [ ] Complete a booking payment
- [ ] Navigate back to payment page URL
- [ ] Verify redirect to success page (idempotent)

### Unauthenticated Access
- [ ] Log out
- [ ] Try to access payment page URL
- [ ] Verify redirect to login page

## Test Scenario 4: Existing Functionality

### Cancel Booking
- [ ] Go to My Bookings
- [ ] Click "Cancel" on a confirmed booking
- [ ] Verify booking status changes to "Cancelled"
- [ ] Verify slot becomes available again

### Extend Booking
- [ ] Go to My Bookings
- [ ] Click "Extend" on an active booking
- [ ] Enter extension time (e.g., 30 minutes)
- [ ] Verify end time is updated

## Test Scenario 5: Responsive Design

### Desktop View
- [ ] Test on desktop browser (1920x1080)
- [ ] Verify split-screen layout on payment page
- [ ] Verify all elements are properly aligned

### Tablet View
- [ ] Test on tablet size (768px width)
- [ ] Verify layout adapts appropriately
- [ ] Verify forms remain usable

### Mobile View
- [ ] Test on mobile size (375px width)
- [ ] Verify single-column layout
- [ ] Verify buttons stack vertically
- [ ] Verify all text is readable

## Test Scenario 6: Browser Compatibility

### Chrome
- [ ] Test complete flow in Chrome
- [ ] Verify all features work

### Firefox
- [ ] Test complete flow in Firefox
- [ ] Verify all features work

### Safari (if available)
- [ ] Test complete flow in Safari
- [ ] Verify all features work

### Edge
- [ ] Test complete flow in Edge
- [ ] Verify all features work

## Visual Verification

### Payment Page Styling
- [ ] Left panel has gradient background
- [ ] Logo and branding are visible
- [ ] Feature icons display correctly
- [ ] Right panel has white background
- [ ] Form fields have proper spacing
- [ ] Booking summary is highlighted
- [ ] Button has hover effect

### Success Page Styling
- [ ] Success icon is green and centered
- [ ] Heading is prominent
- [ ] Details card has proper styling
- [ ] Total paid is highlighted in green
- [ ] Buttons have proper styling
- [ ] Page is centered on screen

## Performance Checks

- [ ] Payment page loads quickly (< 2 seconds)
- [ ] Payment processing is instant
- [ ] Success page loads quickly
- [ ] No console errors in browser
- [ ] No broken images or icons

## Accessibility Checks

- [ ] All form fields have labels
- [ ] Icons have appropriate aria labels
- [ ] Buttons have descriptive text
- [ ] Color contrast is sufficient
- [ ] Tab navigation works correctly
- [ ] Form validation messages are clear

---

## Notes Section

Use this space to record any issues or observations:

```
Date: _______________
Tester: _______________

Issues Found:
1. 
2. 
3. 

Observations:
1. 
2. 
3. 
```

---

## Sign-off

- [ ] All automated tests pass
- [ ] All manual tests pass
- [ ] No critical issues found
- [ ] Feature ready for deployment

**Tested by:** _______________
**Date:** _______________
**Signature:** _______________
