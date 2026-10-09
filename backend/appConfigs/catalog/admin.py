from django.contrib import admin
from .models import Category, Product

# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "business"]

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "business", "category", "price", "is_available"]
    list_filter = ["business", "category", "is_available"]