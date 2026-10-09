from rest_framework import serializers
from .models import Business
from django.contrib.auth import get_user_model
from django.db import transaction
User = get_user_model()

class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ["id", "name", "phone", "created_at"]
        read_only_fields = ["id", "created_at"]
        


class BusinessRegistrationSerializer(serializers.Serializer):
    business_name = serializers.CharField()
    owner_name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A business is already registered with this email.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            first_name=validated_data["owner_name"],
            password=validated_data["password"],
        )
        business = Business.objects.create(
            owner=user, name=validated_data["business_name"], phone=validated_data["phone"]
        )
        return business