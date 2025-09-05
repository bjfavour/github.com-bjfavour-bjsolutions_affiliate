# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import (
    CustomUser, Earnings, Referral, Withdrawal,
    MarketingMaterial, Product, AffiliateLink,
    CashoutRequest, Commission, Order
)

# ✅ LOGIN
class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        identifier = data.get("identifier")
        password = data.get("password")

        try:
            # Try username first
            user = CustomUser.objects.get(username=identifier)
        except CustomUser.DoesNotExist:
            try:
                # Then try phone
                user = CustomUser.objects.get(phone=identifier)
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError("Invalid username/phone or password")

        if not user.is_active:
            raise serializers.ValidationError("Account not approved yet.")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid username/phone or password")

        data["user"] = user
        return data


# ✅ REGISTER
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username", "phone", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        validated_data["is_active"] = False  # Pending approval
        return super().create(validated_data)


# ✅ PROFILE
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "username",
            "full_name",
            "phone",
            "email",
            "bank_name",
            "bank_account",
            "beneficiary_name",
            "profile_picture",
            "balance",
            "referral_code",
            "referred_by",
        ]
        read_only_fields = ["balance", "referral_code", "referred_by"]


# ✅ DASHBOARD
class DashboardSerializer(serializers.Serializer):
    total_earnings = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_referrals = serializers.IntegerField()
    pending_withdrawals = serializers.DecimalField(max_digits=10, decimal_places=2)
    pending_commissions = serializers.DecimalField(max_digits=10, decimal_places=2)

    @staticmethod
    def for_user(user):
        from django.db.models import Sum

        total_earnings = Commission.objects.filter(user=user, status="paid").aggregate(
            total=Sum("amount")
        )["total"] or 0

        pending_commissions = Commission.objects.filter(user=user, status="pending").aggregate(
            total=Sum("amount")
        )["total"] or 0

        total_referrals = Referral.objects.filter(user=user).count()

        pending_withdrawals = CashoutRequest.objects.filter(user=user, status="pending").aggregate(
            total=Sum("requested_amount")
        )["total"] or 0

        return DashboardSerializer({
            "total_earnings": total_earnings,
            "total_referrals": total_referrals,
            "pending_withdrawals": pending_withdrawals,
            "pending_commissions": pending_commissions,
        })


# ✅ COMMISSION HISTORY
class CommissionSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()

    class Meta:
        model = Commission
        fields = ["id", "date", "amount", "status"]

    def get_date(self, obj):
        return obj.created_at.strftime("%Y-%m-%d")


# ✅ CASHOUT HISTORY
class CashoutRequestSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()

    class Meta:
        model = CashoutRequest
        fields = [
            "id",
            "date",
            "requested_amount",
            "processing_fee",
            "net_amount",
            "status",
        ]
        read_only_fields = ["processing_fee", "net_amount", "status", "date"]

    def get_date(self, obj):
        return obj.created_at.strftime("%Y-%m-%d")


# ✅ MARKETING MATERIALS
class MarketingMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketingMaterial
        fields = ["id", "title", "file", "material_type", "uploaded_at"]


# ✅ PRODUCT
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "commission_amount", "picture"]


# ✅ AFFILIATE LINK
class AffiliateLinkSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = AffiliateLink
        fields = ["id", "product", "link"]


# ✅ ORDER
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id", "product", "buyer_name", "buyer_email", "buyer_phone",
            "payment_method", "proof_of_payment", "status", "created_at"
        ]
        read_only_fields = ["status", "created_at"]
