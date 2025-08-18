from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
import uuid


class Earnings(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="earnings"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount}"


class Referral(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="referral_made"
    )
    referred_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="referral_received"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} referred {self.referred_user.username}"


class Withdrawal(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="withdrawals"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} ({self.status})"


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    full_name = models.CharField(max_length=150, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    bank_name = models.CharField(max_length=100, blank=True, null=True)
    bank_account = models.CharField(max_length=50, blank=True, null=True)
    beneficiary_name = models.CharField(max_length=150, blank=True, null=True)

    commission_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # New referral fields
    referral_code = models.CharField(max_length=50, unique=True, blank=True, null=True)
    referred_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="user_referrals"
    )

    REQUIRED_FIELDS = ["email", "phone"]

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        # Auto-generate referral code if not set
        if not self.referral_code:
            self.referral_code = str(uuid.uuid4()).replace("-", "")[:8].upper()
        super().save(*args, **kwargs)


class Commission(models.Model):
    COMMISSION_TYPE = [
        ('flat', 'Flat'),
        ('percent', 'Percent')
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="commissions"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission_type = models.CharField(max_length=10, choices=COMMISSION_TYPE, default='percent')
    status = models.CharField(max_length=20, default="pending")  # pending, paid
    sale_reference = models.CharField(max_length=255, blank=True, null=True)  # link to order
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} ({self.status})"
    
class CashoutRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cashout_requests"
    )
    requested_amount = models.DecimalField(max_digits=10, decimal_places=2)
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Calculate net_amount automatically on save
        self.net_amount = self.requested_amount - self.processing_fee
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} requested {self.requested_amount} ({self.status})"
    
class MarketingMaterial(models.Model):
    MATERIAL_TYPES = [
        ("image", "Image"),
        ("video", "Video"),
        ("pdf", "PDF"),
    ]

    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="marketing_materials/")
    material_type = models.CharField(max_length=10, choices=MATERIAL_TYPES)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.material_type})"
    
class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)
    picture = models.ImageField(upload_to="products/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class AffiliateLink(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    link = models.URLField(blank=True)

    def save(self, *args, **kwargs):
        if not self.link:
            base_url = "http://127.0.0.1:8000"  # change later to your domain
            self.link = f"{base_url}/ref/{self.user.username}/{self.product.id}/"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} → {self.product.name}"
    
# accounts/models.py

class Order(models.Model):
    PAYMENT_METHODS = [
        ("card", "Card"),
        ("bank", "Bank Transfer"),
    ]

    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="orders")
    affiliate = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="orders")  
    buyer_name = models.CharField(max_length=255)
    buyer_email = models.EmailField()
    buyer_phone = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    proof_of_payment = models.ImageField(upload_to="payments/", blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("paid", "Paid"), ("cancelled", "Cancelled")],
        default="pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.product.name}"


