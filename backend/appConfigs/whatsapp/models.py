# whatsapp/models.py
from django.db import models
from businesses.models import Business


class WhatsAppConfiguration(models.Model):
    business = models.OneToOneField(Business, on_delete=models.CASCADE, related_name="whatsapp_config")
    phone_number_id = models.CharField(max_length=50, unique=True)  # Meta's ID, not the phone number itself
    access_token = models.CharField(max_length=512)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.business.name} WhatsApp config"


class ProcessedMessage(models.Model):
    """Dedup table — Meta retries webhook deliveries, this stops double-processing."""
    message_id = models.CharField(max_length=100, unique=True)
    processed_at = models.DateTimeField(auto_now_add=True)