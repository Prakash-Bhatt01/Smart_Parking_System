#!/usr/bin/env python
"""
Create a fresh admin account with known credentials
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_parking.settings')
django.setup()

from django.contrib.auth.models import User

print("=" * 70)
print("CREATING FRESH ADMIN ACCOUNT")
print("=" * 70)

# Delete old admin if exists
old_admin = User.objects.filter(username='admin').first()
if old_admin:
    old_admin.delete()
    print("\n✓ Deleted old admin account")

# Create fresh admin
admin = User.objects.create_superuser(
    username='admin',
    email='admin@smartpark.com',
    password='admin@123',
    first_name='Admin',
    last_name='User'
)

print(f"\n✅ FRESH ADMIN ACCOUNT CREATED")
print("=" * 70)
print(f"\nUsername: admin")
print(f"Password: admin@123")
print(f"Email: admin@smartpark.com")
print(f"\nAdmin Panel: http://127.0.0.1:8000/admin/")
print(f"Login Page: http://127.0.0.1:8000/login/")
print("\n" + "=" * 70)

# Also reset the existing users for consistency
print("\nResetting other user accounts...")

user1 = User.objects.filter(username='User1').first()
if user1:
    user1.set_password('user@123')
    user1.save()
    print(f"✓ User1 password: user@123")

prakz = User.objects.filter(username='Prakz').first()
if prakz:
    prakz.set_password('prakz@123')
    prakz.save()
    print(f"✓ Prakz password: prakz@123")

print("\n" + "=" * 70)
print("ALL USER ACCOUNTS READY")
print("=" * 70)
print("\nLogin Credentials:")
print("  1. Admin: admin / admin@123 (Superuser)")
print("  2. User1: User1 / user@123 (Regular User)")
print("  3. Prakz: Prakz / prakz@123 (Regular User)")
print("\n" + "=" * 70)
