# orders/notifications.py
import logging

from django.core.exceptions import ObjectDoesNotExist

from whatsapp.services import send_text_message

logger = logging.getLogger("whatsapp")

# pending has no message: the customer already got "Order received" at checkout
STATUS_MESSAGES = {
    "confirmed": "✅ Your order *{number}* has been confirmed!\n\nWe're now preparing it.",
    "ready": "📦 Your order *{number}* is ready!",
    "completed": (
        "🎉 Your order *{number}* is complete. Thank you for shopping with {business}!\n\n"
        "Type *menu* anytime to order again."
    ),
}


def notify_status_change(order):
    """Send the customer a WhatsApp message for the order's current status.
    Returns True only if Meta accepted the message. Never raises."""
    template = STATUS_MESSAGES.get(order.status)
    if not template:
        return False

    try:
        config = order.business.whatsapp_config
    except ObjectDoesNotExist:
        logger.warning("Business %s has no WhatsApp config, skipping notification", order.business_id)
        return False
    if not config.is_active:
        return False

    body = template.format(number=order.order_number, business=order.business.name)
    response = send_text_message(
        config.phone_number_id, config.access_token, order.customer.whatsapp_number, body
    )
    return response is not None and response.ok