from django.db import transaction
from django.utils.crypto import get_random_string
from .models import Order, OrderItem


def _generate_order_number(business):
    prefix = "".join(w[0] for w in business.name.split()[:2]).upper() or "ORD"
    last_order = Order.objects.filter(business=business).order_by("-id").first()
    next_seq = (last_order.id + 1) if last_order else 1
    return f"{prefix}-{1000 + next_seq}"


@transaction.atomic
def create_order_from_cart(cart, delivery_address, delivery_fee=0):
    if not cart.items.exists():
        raise ValueError("Cannot check out an empty cart.")

    # lock the products being ordered so stock checks are consistent under concurrent orders
    for item in cart.items.select_related("product"):
        product = item.product
        product.refresh_from_db()
        if product.stock_quantity < item.quantity:
            raise ValueError(f"{product.name} only has {product.stock_quantity} {product.unit} left.")

    subtotal = cart.total()
    order = Order.objects.create(
        business=cart.business,
        customer=cart.customer,
        order_number=_generate_order_number(cart.business),
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        total=subtotal + delivery_fee,
        delivery_address=delivery_address,
    )

    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            product_name=item.product.name,
            quantity=item.quantity,
            unit_price=item.unit_price,
            subtotal=item.subtotal(),
        )
        item.product.stock_quantity -= item.quantity
        item.product.save()

    cart.status = "checked_out"
    cart.save()

    return order