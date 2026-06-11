#!/usr/bin/env python
"""
Diagnostic script to test login, logout, and admin functionality
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_parking.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

print("=" * 70)
print("AUTHENTICATION DIAGNOSTICS")
print("=" * 70)

# Create test client
client = Client()

# Test 1: Check if admin user exists
print("\n1. Checking for superuser...")
admin = User.objects.filter(is_superuser=True).first()
if admin:
    print(f"   ✓ Superuser found: {admin.username}")
else:
    print("   ⚠ No superuser found. Creating one...")
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )
    print(f"   ✓ Created superuser: {admin.username} / password: admin123")

# Test 2: Check if regular user exists
print("\n2. Checking for regular user...")
regular_user = User.objects.filter(is_superuser=False).first()
if not regular_user:
    print("   Creating test user...")
    regular_user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )
    print(f"   ✓ Created user: {regular_user.username} / password: testpass123")
else:
    print(f"   ✓ Regular user found: {regular_user.username}")

# Test 3: Test login view GET
print("\n3. Testing login page (GET)...")
try:
    response = client.get('/login/')
    if response.status_code == 200:
        print(f"   ✓ Login page loads successfully (status: {response.status_code})")
    else:
        print(f"   ✗ Login page error (status: {response.status_code})")
except Exception as e:
    print(f"   ✗ Error accessing login page: {e}")

# Test 4: Test login POST
print("\n4. Testing login POST...")
try:
    response = client.post('/login/', {
        'username': regular_user.username,
        'password': 'testpass123'
    })
    if response.status_code == 302:  # Redirect after successful login
        print(f"   ✓ Login successful (redirect to: {response.url})")
    else:
        print(f"   ✗ Login failed (status: {response.status_code})")
except Exception as e:
    print(f"   ✗ Error during login POST: {e}")

# Test 5: Check if user is authenticated
print("\n5. Checking authentication state...")
if '_auth_user_id' in client.session:
    print(f"   ✓ User is authenticated (session user_id: {client.session['_auth_user_id']})")
else:
    print("   ✗ User is NOT authenticated in session")

# Test 6: Test accessing protected page
print("\n6. Testing protected page access...")
try:
    response = client.get('/search/')
    if response.status_code == 200:
        print(f"   ✓ Can access protected page (status: {response.status_code})")
    elif response.status_code == 302:
        print(f"   ⚠ Redirected to login (status: {response.status_code}, redirect: {response.url})")
    else:
        print(f"   ✗ Unexpected status: {response.status_code}")
except Exception as e:
    print(f"   ✗ Error accessing protected page: {e}")

# Test 7: Test logout (GET)
print("\n7. Testing logout (GET)...")
try:
    response = client.get('/logout/')
    if response.status_code == 302:
        print(f"   ✓ Logout GET works (redirects to: {response.url})")
    else:
        print(f"   Status: {response.status_code}")
except Exception as e:
    print(f"   ✗ Error during logout GET: {e}")

# Test 8: Re-login and test logout POST
print("\n8. Testing logout (POST)...")
client.post('/login/', {'username': regular_user.username, 'password': 'testpass123'})
try:
    response = client.post('/logout/')
    if response.status_code == 302:
        print(f"   ✓ Logout POST works (redirects to: {response.url})")
    else:
        print(f"   Status: {response.status_code}")
except Exception as e:
    print(f"   ✗ Error during logout POST: {e}")

# Test 9: Check session after logout
print("\n9. Checking authentication after logout...")
if '_auth_user_id' in client.session:
    print(f"   ✗ User still in session after logout (user_id: {client.session['_auth_user_id']})")
else:
    print("   ✓ User successfully logged out (no session)")

# Test 10: Test admin login
print("\n10. Testing admin login...")
admin_client = Client()
try:
    response = admin_client.post('/login/', {
        'username': admin.username,
        'password': 'admin123'
    })
    if response.status_code == 302:
        print(f"   ✓ Admin login successful")
        # Try to access admin panel
        admin_response = admin_client.get('/admin/')
        if admin_response.status_code == 200:
            print(f"   ✓ Can access admin panel")
        else:
            print(f"   ⚠ Admin panel status: {admin_response.status_code}")
    else:
        print(f"   ✗ Admin login failed (status: {response.status_code})")
except Exception as e:
    print(f"   ✗ Error during admin login: {e}")

print("\n" + "=" * 70)
print("DIAGNOSTIC SUMMARY")
print("=" * 70)
print(f"\nSuperuser: {admin.username} / password: admin123")
print(f"Test User: {regular_user.username} / password: testpass123")
print("\nTo test manually:")
print("1. Run: python manage.py runserver")
print("2. Visit: http://127.0.0.1:8000/login/")
print("3. Visit: http://127.0.0.1:8000/admin/")
print("\n" + "=" * 70)
