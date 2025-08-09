# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=150, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    bank_name = models.CharField(max_length=100, blank=True, null=True)
    bank_account = models.CharField(max_length=50, blank=True, null=True)
    beneficiary_name = models.CharField(max_length=150, blank=True, null=True)

    commission_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    REQUIRED_FIELDS = ["email", "phone"]

    def __str__(self):
        return self.username
