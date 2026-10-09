from django.db import models
from businesses.models import Business

# Create your models here.
class Customer(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="customers")
    whatsapp_number = models.CharField(max_length=20)
    name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["business", "whatsapp_number"], name="unique_customer_per_business"
            )
        ]
        
    def save(self, *args, **kwargs):
        self.whatsapp_number = self.whatsapp_number.lstrip("+").replace(" ", "")
        super().save(*args, **kwargs)