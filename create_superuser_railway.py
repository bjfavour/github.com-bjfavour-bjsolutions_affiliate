import os
import django

# Set your settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bjsolutions.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Change these credentials to whatever you want
USERNAME = "admin"
EMAIL = "admin@example.com"
PASSWORD = "Loveme4177@@"

if not User.objects.filter(username=USERNAME).exists():
    User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
    print(f"Superuser '{USERNAME}' created successfully!")
else:
    print(f"Superuser '{USERNAME}' already exists.")
