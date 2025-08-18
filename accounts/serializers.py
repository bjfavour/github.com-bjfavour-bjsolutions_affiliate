# accounts/serializers.py
from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.hashers import make_password
from .models import Earnings, Referral, Withdrawal
from .models import MarketingMaterial, Product, AffiliateLink, CashoutRequest
from .models import Order


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        identifier = data.get("identifier")
        password = data.get("password")

        try:
            # Try to find user by username or phone
            user = CustomUser.objects.get(username=identifier)
        except CustomUser.DoesNotExist:
            try:
                user = CustomUser.objects.get(phone=identifier)
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError("Invalid username/phone or password")

        if not user.is_active:
            raise serializers.ValidationError("Account not approved yet.")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid username/phone or password")

        data["user"] = user
        return data

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username", "phone", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        validated_data["is_active"] = False  # Pending approval
        return super().create(validated_data)
    
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username", "phone", "email", "balance", "referral_code", "referred_by"]
        read_only_fields = ["balance", "referral_code", "referred_by"]

class DashboardSerializer(serializers.Serializer):
    total_earnings = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_referrals = serializers.IntegerField()
    pending_withdrawals = serializers.DecimalField(max_digits=10, decimal_places=2)
    pending_commissions = serializers.DecimalField(max_digits=10, decimal_places=2) 
    
from rest_framework import serializers
from .models import CashoutRequest

class CashoutRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashoutRequest
        fields = ['id', 'requested_amount', 'processing_fee', 'net_amount', 'status', 'created_at']
        read_only_fields = ['processing_fee', 'net_amount', 'status', 'created_at']
        
        
class MarketingMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketingMaterial
        fields = ["id", "title", "file", "material_type", "uploaded_at"]
        
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "commission_amount", "picture"]

class AffiliateLinkSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = AffiliateLink
        fields = ["id", "product", "link"]
        
        
# accounts/serializers.py
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id", "product", "buyer_name", "buyer_email", "buyer_phone",
            "payment_method", "proof_of_payment", "status", "created_at"
        ]
        read_only_fields = ["status", "created_at"]



