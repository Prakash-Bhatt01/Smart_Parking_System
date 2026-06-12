#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Create default admin user if none exists
python manage.py create_default_admin

echo "✅ Build completed successfully!"
