# accounts/serializers.py
from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.hashers import make_password

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
