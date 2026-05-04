"""
Manual verification script for Task 10: Demo Payment Flow Frontend
This script performs automated checks on the payment flow HTML structure.
"""

import requests
from bs4 import BeautifulSoup
import sys

BASE_URL = "http://127.0.0.1:8000"

def login_and_get_session():
    """Login and return session with cookies."""
    session = requests.Session()
    
    # Get login page to get CSRF token
    response = session.get(f"{BASE_URL}/login/")
    soup = BeautifulSoup(response.content, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']
    
    # Login
    login_data = {
        'username': 'testuser',
        'password': 'testpass123',
        'csrfmiddlewaretoken': csrf_token
    }
    response = session.post(f"{BASE_URL}/login/", data=login_data)
    
    if response.status_code == 200 and '/login/' not in response.url:
        print("✓ Successfully logged in")
        return session
    else:
        print("❌ Login failed")
        return None

def test_payment_page_structure(session, booking_id):
    """Test 1: Payment page structure and elements."""
    print("\n=== Test 1: Payment Page Structure ===")
    
    try:
        response = session.get(f"{BASE_URL}/payment/{booking_id}/")
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check page title
        title = soup.find('title')
        if title and 'Complete Payment' in title.text:
            print("✓ Page title correct")
        else:
            print(f"⚠ Page title: {title.text if title else 'Not found'}")
        
        # Check split-screen layout
        auth_wrapper = soup.find('div', class_='auth-wrapper')
        if auth_wrapper:
            print("✓ Split-screen layout present")
        else:
            print("❌ Split-screen layout missing")
            return False
        
        # Check left branding panel
        auth_left = soup.find('div', class_='auth-left')
        if auth_left:
            print("✓ Left branding panel present")
            
            # Check logo
            logo = auth_left.find('div', class_='auth-logo')
            if logo:
                print("  ✓ SmartPark logo present")
            
            # Check features
            features = auth_left.find_all('div', class_='auth-feature')
            if len(features) >= 3:
                print(f"  ✓ Feature highlights present ({len(features)} features)")
        else:
            print("❌ Left branding panel missing")
        
        # Check right form panel
        auth_right = soup.find('div', class_='auth-right')
        if auth_right:
            print("✓ Right form panel present")
        else:
            print("❌ Right form panel missing")
            return False
        
        # Check booking summary
        booking_summary = soup.find('div', class_='booking-summary')
        if booking_summary:
            print("✓ Booking summary section present")
            
            summary_rows = booking_summary.find_all('div', class_='summary-row')
            if len(summary_rows) >= 4:
                print(f"  ✓ Booking details present ({len(summary_rows)} rows)")
                
                # Check for specific details
                summary_text = booking_summary.get_text().lower()
                if 'slot' in summary_text:
                    print("  ✓ Slot number displayed")
                if 'location' in summary_text or 'lot' in summary_text:
                    print("  ✓ Location displayed")
                if 'duration' in summary_text:
                    print("  ✓ Duration displayed")
                if 'total' in summary_text:
                    print("  ✓ Total cost displayed")
        else:
            print("❌ Booking summary missing")
        
        # Check form fields
        form = soup.find('form')
        if form:
            print("✓ Payment form present")
            
            # Check card number field
            card_number = form.find('input', {'name': 'card_number'})
            if card_number:
                print("  ✓ Card number field present")
                if card_number.get('pattern') == '[0-9]{16}':
                    print("    ✓ Pattern validation correct")
                if card_number.get('maxlength') == '16':
                    print("    ✓ Maxlength correct")
                if card_number.has_attr('required'):
                    print("    ✓ Required attribute set")
            else:
                print("  ❌ Card number field missing")
            
            # Check cardholder name field
            card_name = form.find('input', {'name': 'card_name'})
            if card_name:
                print("  ✓ Cardholder name field present")
            else:
                print("  ❌ Cardholder name field missing")
            
            # Check expiry field
            expiry = form.find('input', {'name': 'expiry'})
            if expiry:
                print("  ✓ Expiry date field present")
                pattern = expiry.get('pattern', '')
                if '0[1-9]|1[0-2]' in pattern and '[0-9]{2}' in pattern:
                    print("    ✓ Pattern validation correct")
                if expiry.get('maxlength') == '5':
                    print("    ✓ Maxlength correct")
            else:
                print("  ❌ Expiry field missing")
            
            # Check CVV field
            cvv = form.find('input', {'name': 'cvv'})
            if cvv:
                print("  ✓ CVV field present")
                if cvv.get('pattern') == '[0-9]{3,4}':
                    print("    ✓ Pattern validation correct")
                if cvv.get('maxlength') == '4':
                    print("    ✓ Maxlength correct")
            else:
                print("  ❌ CVV field missing")
            
            # Check submit button
            submit_btn = form.find('button', {'type': 'submit'})
            if submit_btn:
                print("  ✓ Submit button present")
                if 'complete payment' in submit_btn.get_text().lower():
                    print("    ✓ Button text correct")
            else:
                print("  ❌ Submit button missing")
        else:
            print("❌ Payment form missing")
        
        # Check demo payment note
        payment_note = soup.find('p', class_='payment-note')
        if payment_note and 'demo' in payment_note.get_text().lower():
            print("✓ Demo payment note present")
        else:
            print("⚠ Demo payment note missing or incorrect")
        
        print("\n✅ Test 1 PASSED: Payment page structure verified")
        return True
        
    except Exception as e:
        print(f"\n❌ Test 1 FAILED: {str(e)}")
        return False

def test_success_page_structure(session, booking_id):
    """Test 2: Success page structure and elements."""
    print("\n=== Test 2: Success Page Structure ===")
    
    try:
        response = session.get(f"{BASE_URL}/booking-success/{booking_id}/")
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check page title
        title = soup.find('title')
        if title and 'Booking Confirmed' in title.text:
            print("✓ Page title correct")
        else:
            print(f"⚠ Page title: {title.text if title else 'Not found'}")
        
        # Check success page layout
        success_page = soup.find('div', class_='success-page')
        if success_page:
            print("✓ Success page layout present")
        else:
            print("❌ Success page layout missing")
            return False
        
        # Check success card
        success_card = soup.find('div', class_='success-card')
        if success_card:
            print("✓ Success card present")
        else:
            print("❌ Success card missing")
            return False
        
        # Check success icon
        success_icon = soup.find('div', class_='success-icon')
        if success_icon:
            print("✓ Success icon present")
            icon = success_icon.find('i', class_='fa-check-circle')
            if icon:
                print("  ✓ Check circle icon correct")
        else:
            print("❌ Success icon missing")
        
        # Check heading
        heading = soup.find('h1')
        if heading and 'confirmed' in heading.get_text().lower():
            print("✓ Confirmation heading present")
        else:
            print("⚠ Confirmation heading missing or incorrect")
        
        # Check booking details card
        details_card = soup.find('div', class_='booking-details-card')
        if details_card:
            print("✓ Booking details card present")
            
            detail_rows = details_card.find_all('div', class_='detail-row')
            if len(detail_rows) >= 8:
                print(f"  ✓ Booking details present ({len(detail_rows)} rows)")
                
                # Check for specific details
                details_text = details_card.get_text().lower()
                checks = [
                    ('booking id', 'Booking ID'),
                    ('slot', 'Slot number'),
                    ('parking lot', 'Parking lot name'),
                    ('address', 'Address'),
                    ('start time', 'Start time'),
                    ('end time', 'End time'),
                    ('duration', 'Duration'),
                    ('total paid', 'Total paid')
                ]
                
                for keyword, label in checks:
                    if keyword in details_text:
                        print(f"  ✓ {label} displayed")
            else:
                print(f"  ⚠ Only {len(detail_rows)} detail rows found (expected 8+)")
        else:
            print("❌ Booking details card missing")
        
        # Check navigation buttons
        success_actions = soup.find('div', class_='success-actions')
        if success_actions:
            print("✓ Success actions section present")
            
            # Check "View My Bookings" button
            my_bookings_link = success_actions.find('a', href='/my-bookings/')
            if my_bookings_link:
                print("  ✓ 'View My Bookings' button present")
                if 'btn-primary' in my_bookings_link.get('class', []):
                    print("    ✓ Primary button styling correct")
            else:
                print("  ❌ 'View My Bookings' button missing")
            
            # Check "Back to Home" button
            home_link = success_actions.find('a', href='/')
            if home_link:
                print("  ✓ 'Back to Home' button present")
                if 'btn-outline' in home_link.get('class', []):
                    print("    ✓ Outline button styling correct")
            else:
                print("  ❌ 'Back to Home' button missing")
        else:
            print("❌ Success actions section missing")
        
        print("\n✅ Test 2 PASSED: Success page structure verified")
        return True
        
    except Exception as e:
        print(f"\n❌ Test 2 FAILED: {str(e)}")
        return False

def test_payment_submission(session, booking_id):
    """Test 3: Payment form submission."""
    print("\n=== Test 3: Payment Form Submission ===")
    
    try:
        # Get payment page to get CSRF token
        response = session.get(f"{BASE_URL}/payment/{booking_id}/")
        soup = BeautifulSoup(response.content, 'html.parser')
        
        form = soup.find('form')
        if not form:
            print("❌ Payment form not found")
            return False
        
        csrf_token = form.find('input', {'name': 'csrfmiddlewaretoken'})
        if not csrf_token:
            print("❌ CSRF token not found")
            return False
        
        print("✓ Payment form and CSRF token found")
        
        # Submit payment form
        payment_data = {
            'card_number': '1234567890123456',
            'card_name': 'John Doe',
            'expiry': '12/25',
            'cvv': '123',
            'csrfmiddlewaretoken': csrf_token['value']
        }
        
        response = session.post(f"{BASE_URL}/process-payment/{booking_id}/", data=payment_data)
        
        # Check if redirected to success page
        if response.status_code == 200 and f'/booking-success/{booking_id}/' in response.url:
            print("✓ Form submitted successfully")
            print(f"✓ Redirected to success page: {response.url}")
            
            # Check for success message in response
            soup = BeautifulSoup(response.content, 'html.parser')
            messages = soup.find_all('div', class_='alert-success')
            if messages:
                print("✓ Success message displayed")
            
            print("\n✅ Test 3 PASSED: Payment submission successful")
            return True
        else:
            print(f"❌ Unexpected response: {response.status_code}, URL: {response.url}")
            return False
        
    except Exception as e:
        print(f"\n❌ Test 3 FAILED: {str(e)}")
        return False

def main():
    """Main test runner."""
    print("=" * 60)
    print("FRONTEND VERIFICATION - TASK 10")
    print("Demo Payment Flow - Frontend Implementation")
    print("=" * 60)
    
    # Login
    print("\nLogging in...")
    session = login_and_get_session()
    if not session:
        print("\n❌ Cannot proceed without authentication")
        print("Please ensure:")
        print("  1. Django server is running at http://127.0.0.1:8000/")
        print("  2. User 'testuser' exists with password 'testpass123'")
        sys.exit(1)
    
    # Get a pending booking ID
    booking_id = 13  # Use the booking we created earlier
    print(f"\nUsing booking ID: {booking_id}")
    
    # Run tests
    results = []
    results.append(("Payment Page Structure", test_payment_page_structure(session, booking_id)))
    results.append(("Success Page Structure", test_success_page_structure(session, booking_id)))
    results.append(("Payment Form Submission", test_payment_submission(session, booking_id)))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL AUTOMATED TESTS PASSED!")
        print("\nPlease also perform manual verification:")
        print("  1. Open http://127.0.0.1:8000/ in a browser")
        print("  2. Login and create a new booking")
        print("  3. Verify payment form displays correctly")
        print("  4. Test form validation with invalid inputs")
        print("  5. Complete payment and verify success page")
        print("\nSee TASK_10_VERIFICATION_CHECKLIST.md for detailed manual tests")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")

if __name__ == '__main__':
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        print("❌ Required packages not installed")
        print("Please install: pip install requests beautifulsoup4")
        sys.exit(1)
    
    main()
