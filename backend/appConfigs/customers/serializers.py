from rest_framework import serializers
from .models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    orders_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = ["id", "name", "whatsapp_number", "orders_count", "created_at"]