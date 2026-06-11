#!/usr/bin/env python
"""
Reset passwords for existing users to known values
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_parking.settings')
django.setup()

from django.contrib.auth.models import User

print("=" * 70)
print("RESETTING USER PASSWORDS")
print("=" * 70)

# Reset admin password
admin = User.objects.filter(username='admin').first()
if admin:
    admin.set_password('admin123')
    admin.save()
    print(f"\n✓ Admin password reset")
    print(f"   Username: admin")
    print(f"   Password: admin123")

# Reset User1 password
user1 = User.objects.filter(username='User1').first()
if user1:
    user1.set_password('user123')
    user1.save()
    print(f"\n✓ User1 password reset")
    print(f"   Username: User1")
    print(f"   Password: user123")

# Reset Prakz password
prakz = User.objects.filter(username='Prakz').first()
if prakz:
    prakz.set_password('prakz123')
    prakz.save()
    print(f"\n✓ Prakz password reset")
    print(f"   Username: Prakz")
    print(f"   Password: prakz123")

print("\n" + "=" * 70)
print("PASSWORDS RESET SUCCESSFULLY")
print("=" * 70)
print("\nYou can now login with:")
print("  - admin / admin123 (superuser)")
print("  - User1 / user123 (regular user)")
print("  - Prakz / prakz123 (regular user)")
print("\n" + "=" * 70)
