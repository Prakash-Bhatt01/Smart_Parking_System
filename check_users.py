#!/usr/bin/env python
"""
Check existing users and verify passwords
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_parking.settings')
django.setup()

from django.contrib.auth.models import User

print("=" * 70)
print("EXISTING USERS IN DATABASE")
print("=" * 70)

users = User.objects.all()
print(f"\nTotal users: {users.count()}\n")

for user in users:
    print(f"Username: {user.username}")
    print(f"  - Email: {user.email}")
    print(f"  - First Name: {user.first_name}")
    print(f"  - Last Name: {user.last_name}")
    print(f"  - Is Superuser: {user.is_superuser}")
    print(f"  - Is Staff: {user.is_staff}")
    print(f"  - Is Active: {user.is_active}")
    print(f"  - Date Joined: {user.date_joined}")
    
    # Test password
    test_passwords = ['admin123', 'testpass123', 'password', 'admin']
    for pwd in test_passwords:
        if user.check_password(pwd):
            print(f"  ✓ Password: {pwd}")
            break
    else:
        print(f"  ⚠ Password: Unknown (not in test list)")
    print()

print("=" * 70)
print("\nTo reset a password, run:")
print("python manage.py changepassword <username>")
print("=" * 70)
