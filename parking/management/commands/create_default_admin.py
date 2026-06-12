"""
Management command to create a default superuser if none exists.
Usage: python manage.py create_default_admin
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Creates a default superuser if no superuser exists'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Check if any superuser exists
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(
                self.style.WARNING('Superuser already exists. Skipping creation.')
            )
            return
        
        # Create default superuser
        try:
            user = User.objects.create_superuser(
                username='admin',
                email='admin@smartpark.com',
                password='smartpark2026',  # Change this in production!
                first_name='Admin',
                last_name='User'
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Successfully created superuser: {user.username}'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    '\n⚠️  SECURITY WARNING:'
                    '\nDefault credentials created:'
                    '\n  Username: admin'
                    '\n  Password: smartpark2026'
                    '\n\nChange the password immediately using:'
                    '\n  python manage.py changepassword admin'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser: {str(e)}')
            )
