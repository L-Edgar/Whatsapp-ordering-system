# whatsapp/admin.py
from django.contrib import admin
from .models import WhatsAppConfiguration

@admin.register(WhatsAppConfiguration)
class WhatsAppConfigAdmin(admin.ModelAdmin):
    list_display = ["business", "phone_number_id", "is_active"]