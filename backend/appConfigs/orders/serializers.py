# orders/serializers.py
from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "product_name", "quantity", "unit_price", "subtotal"]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    customer_phone = serializers.CharField(source="customer.whatsapp_number", read_only=True)

    class Meta:
        model = Order
        fields = ["id", "order_number", "status", "customer_name", "customer_phone",
                  "subtotal", "delivery_fee", "total", "delivery_address", "items", "created_at"]
        read_only_fields = ["order_number", "subtotal", "total"]