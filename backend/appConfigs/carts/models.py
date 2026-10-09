from django.db import models
from businesses.models import Business
from customers.models import Customer
from catalog.models import Product


class Cart(models.Model):
    STATUS_CHOICES = [("open", "Open"), ("checked_out", "Checked Out"), ("abandoned", "Abandoned")]

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="carts")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="carts")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    created_at = models.DateTimeField(auto_now_add=True)

    def total(self):
        return sum(item.subtotal() for item in self.items.all())

    def __str__(self):
        return f"Cart #{self.id} ({self.customer})"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["cart", "product"], name="unique_product_per_cart")
        ]

    def subtotal(self):
        return self.quantity * self.unit_price