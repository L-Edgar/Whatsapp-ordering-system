from rest_framework import serializers
from .models import Category, Product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "category", "description", "price", "unit",
                  "stock_quantity", "image", "is_available", "created_at"]
        read_only_fields = ["id", "created_at"]