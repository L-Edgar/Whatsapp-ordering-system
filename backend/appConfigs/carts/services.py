from django.db import transaction
from .models import Cart, CartItem


def get_or_create_open_cart(business, customer):
    cart, _ = Cart.objects.get_or_create(
        business=business, customer=customer, status="open"
    )
    return cart


@transaction.atomic
def add_item(cart, product, quantity):
    if product.stock_quantity < quantity:
        raise ValueError(f"Only {product.stock_quantity} {product.unit} of {product.name} left in stock.")

    item, created = CartItem.objects.get_or_create(
        cart=cart, product=product,
        defaults={"quantity": quantity, "unit_price": product.price},
    )
    if not created:
        item.quantity += quantity
        item.unit_price = product.price  # keep price current while still in cart
        item.save()
    return item


def remove_item(cart, product):
    CartItem.objects.filter(cart=cart, product=product).delete()


def clear_cart(cart):
    cart.items.all().delete()