import logging
from decimal import Decimal

from django.conf import settings

from carts.services import get_or_create_open_cart, add_item, clear_cart
from catalog.models import Category, Product
from customers.models import Customer
from orders.models import Order
from orders.services import create_order_from_cart

from . import services as wa
from .models import ConversationState, WhatsAppConfiguration

logger = logging.getLogger("whatsapp")

DELIVERY_FEE = getattr(settings, "DELIVERY_FEE", 5000)
GREETINGS = {"hi", "hello", "hey", "menu", "start", "restart", "0"}


def ugx(amount):
    return f"UGX {Decimal(amount):,.0f}"


class Session:
    """Everything a handler needs: who's talking, which business, and how to reply."""

    def __init__(self, config, customer, convo):
        self.config = config
        self.business = config.business
        self.customer = customer
        self.convo = convo

    @property
    def ctx(self):
        return self.convo.context or {}

    def go(self, state, **context):
        """Move to a new state. Context is replaced, so pass anything you want to keep."""
        self.convo.state = state
        self.convo.context = context
        self.convo.save()

    def text(self, body):
        wa.send_text_message(
            self.config.phone_number_id, self.config.access_token,
            self.customer.whatsapp_number, body,
        )

    def buttons(self, body, buttons):
        """buttons: list of (id, title) tuples, max 3."""
        wa.send_button_message(
            self.config.phone_number_id, self.config.access_token,
            self.customer.whatsapp_number, body,
            [{"id": i, "title": t[:20]} for i, t in buttons],
        )

    def list(self, body, button_text, rows):
        wa.send_list_message(
            self.config.phone_number_id, self.config.access_token,
            self.customer.whatsapp_number, body, button_text, rows,
        )


# ---------------------------------------------------------------- entry point

def handle_incoming_message(phone_number_id, from_number, text, action_id, profile_name=""):
    config = (
        WhatsAppConfiguration.objects.select_related("business")
        .filter(phone_number_id=phone_number_id, is_active=True)
        .first()
    )
    if not config:
        logger.warning("No active WhatsApp config for phone_number_id=%s", phone_number_id)
        return

    number = from_number.lstrip("+").replace(" ", "")
    customer, _ = Customer.objects.get_or_create(
        business=config.business,
        whatsapp_number=number,
        defaults={"name": profile_name},
    )
    convo, _ = ConversationState.objects.get_or_create(customer=customer)
    s = Session(config, customer, convo)
    text = (text or "").strip()

    # "hi" / "menu" always works, from any state
    if not action_id and text.lower() in GREETINGS:
        return show_main_menu(s)

    # button and list taps are routed by id, regardless of state
    if action_id and route_action(s, action_id):
        return

    # otherwise, free text goes to whatever the current state is waiting for
    handler = TEXT_HANDLERS.get(convo.state)
    if handler:
        return handler(s, text)

    s.text("Sorry, I didn't catch that. Type *menu* to see your options.")


def route_action(s, action_id):
    """Returns True if the action was handled."""
    if action_id == "menu:shop" or action_id == "cart:more":
        show_categories(s)
    elif action_id == "menu:orders":
        show_orders(s)
    elif action_id == "menu:help":
        show_help(s)
    elif action_id.startswith("cat:"):
        show_products(s, action_id.split(":", 1)[1])
    elif action_id.startswith("prod:"):
        ask_quantity(s, action_id.split(":", 1)[1])
    elif action_id == "cart:view":
        show_cart(s)
    elif action_id == "cart:checkout":
        start_checkout(s)
    elif action_id == "cart:clear":
        cart = get_or_create_open_cart(s.business, s.customer)
        clear_cart(cart)
        s.text("🗑️ Your cart is empty.")
        show_main_menu(s)
    elif action_id in ("order:confirm", "order:cancel"):
        handle_order_decision(s, action_id)
    else:
        return False
    return True


# ---------------------------------------------------------------- main menu etc.

def show_main_menu(s):
    s.go("MAIN_MENU")
    s.buttons(
        f"👋 Welcome to {s.business.name}!\n\nWhat would you like to do?",
        [("menu:shop", "🛒 Shop"), ("menu:orders", "📦 My Orders"), ("menu:help", "❓ Help")],
    )


def show_help(s):
    s.go("MAIN_MENU")
    s.text(
        f"Here's how ordering from {s.business.name} works:\n\n"
        "1. Tap *Shop* and pick a category\n"
        "2. Choose a product and tell us how many\n"
        "3. Check out with your delivery address\n\n"
        "Type *menu* at any time to start over. Your cart is saved."
    )


def show_orders(s):
    orders = Order.objects.filter(customer=s.customer).order_by("-created_at")[:5]
    if not orders:
        s.text("You haven't placed any orders yet. Type *menu* and tap Shop to start.")
        return
    lines = [f"*{o.order_number}* — {ugx(o.total)}\nStatus: {o.get_status_display()}" for o in orders]
    s.text("📦 *Your recent orders*\n\n" + "\n\n".join(lines))


# ---------------------------------------------------------------- browsing

def show_categories(s):
    categories = (
        Category.objects.filter(
            business=s.business,
            products__is_available=True,
            products__stock_quantity__gt=0,
        ).distinct()[:10]
    )
    if not categories:
        s.text("Nothing is available to order right now. Please check back soon!")
        return
    s.go("CATEGORY_SELECTION")
    s.list(
        "What would you like to shop for?",
        "Browse",
        [{"id": f"cat:{c.id}", "title": c.name, "description": c.description} for c in categories],
    )


def show_products(s, category_id):
    category = Category.objects.filter(business=s.business, id=category_id).first()
    if not category:
        return show_categories(s)
    products = Product.objects.filter(
        business=s.business, category=category, is_available=True, stock_quantity__gt=0
    )[:10]
    if not products:
        s.text(f"No products available in {category.name} right now.")
        return show_categories(s)
    s.go("PRODUCT_SELECTION", category_id=category.id)
    s.list(
        f"*{category.name}* — pick a product:",
        "See products",
        [
            {"id": f"prod:{p.id}", "title": p.name, "description": f"{ugx(p.price)} / {p.unit}"}
            for p in products
        ],
    )


def ask_quantity(s, product_id):
    product = Product.objects.filter(
        business=s.business, id=product_id, is_available=True
    ).first()
    if not product:
        s.text("Sorry, that product is no longer available.")
        return show_categories(s)
    s.go("QUANTITY_INPUT", product_id=product.id)
    s.text(
        f"*{product.name}* — {ugx(product.price)} / {product.unit}\n"
        f"{product.stock_quantity} {product.unit} available.\n\n"
        f"How many {product.unit} would you like? Reply with a number."
    )


def handle_quantity(s, text):
    product = Product.objects.filter(business=s.business, id=s.ctx.get("product_id")).first()
    if not product:
        return show_categories(s)
    if not text.isdigit() or int(text) < 1:
        return s.text("Please reply with a whole number, like *2*.")

    quantity = int(text)
    cart = get_or_create_open_cart(s.business, s.customer)
    try:
        add_item(cart, product, quantity)
    except ValueError as exc:
        return s.text(f"⚠️ {exc}\nTry a smaller number, or type *menu* to go back.")

    s.go("CART_MENU")
    s.buttons(
        f"✅ Added {quantity} {product.unit} of {product.name}.\n\nWhat would you like to do next?",
        [("cart:more", "🛒 Keep shopping"), ("cart:view", "👀 View cart"), ("cart:checkout", "✅ Checkout")],
    )


# ---------------------------------------------------------------- cart

def cart_lines(cart):
    return [
        f"• {i.product.name} — {i.quantity} {i.product.unit} × {ugx(i.unit_price)} = {ugx(i.subtotal())}"
        for i in cart.items.select_related("product")
    ]


def show_cart(s):
    cart = get_or_create_open_cart(s.business, s.customer)
    if not cart.items.exists():
        s.go("MAIN_MENU")
        return s.buttons("🛒 Your cart is empty.", [("menu:shop", "🛒 Start shopping")])
    s.go("CART_VIEW")
    s.buttons(
        "🛒 *Your cart*\n\n" + "\n".join(cart_lines(cart)) + f"\n\n*Total: {ugx(cart.total())}*",
        [("cart:more", "➕ Add more"), ("cart:checkout", "✅ Checkout"), ("cart:clear", "❌ Clear cart")],
    )


# ---------------------------------------------------------------- checkout

def start_checkout(s):
    cart = get_or_create_open_cart(s.business, s.customer)
    if not cart.items.exists():
        return show_cart(s)
    if not s.customer.name:
        s.go("CHECKOUT_NAME")
        return s.text("What's your name?")
    ask_address(s)


def handle_name(s, text):
    if len(text) < 2:
        return s.text("Please enter your name.")
    s.customer.name = text[:255]
    s.customer.save()
    ask_address(s)


def ask_address(s):
    s.go("CHECKOUT_ADDRESS")
    s.text("📍 Where should we deliver your order?\n\nPlease type your area and a landmark, e.g. _Ntinda, near St Luke Church_.")


def handle_address(s, text):
    if len(text) < 5:
        return s.text("Please give a bit more detail so we can find you.")
    cart = get_or_create_open_cart(s.business, s.customer)
    if not cart.items.exists():
        return show_cart(s)

    subtotal = cart.total()
    s.go("CHECKOUT_CONFIRM", address=text)
    s.buttons(
        "🧾 *ORDER SUMMARY*\n\n"
        + "\n".join(cart_lines(cart))
        + f"\n\nSubtotal: {ugx(subtotal)}"
        + f"\nDelivery: {ugx(DELIVERY_FEE)}"
        + f"\n*Total: {ugx(subtotal + DELIVERY_FEE)}*"
        + f"\n\nDeliver to: {text}\n\nPlace this order?",
        [("order:confirm", "✅ Confirm"), ("order:cancel", "❌ Cancel")],
    )


def handle_order_decision(s, action_id):
    if s.convo.state != "CHECKOUT_CONFIRM":
        s.text("That order request has expired.")
        return show_main_menu(s)

    if action_id == "order:cancel":
        s.text("Order cancelled. Your cart is still saved.")
        return show_main_menu(s)

    cart = get_or_create_open_cart(s.business, s.customer)
    try:
        order = create_order_from_cart(
            cart, delivery_address=s.ctx.get("address", ""), delivery_fee=DELIVERY_FEE
        )
    except ValueError as exc:
        s.text(f"⚠️ We couldn't place your order: {exc}")
        return show_cart(s)

    s.go("MAIN_MENU")
    s.text(
        f"🎉 *Order {order.order_number} received!*\n\n"
        f"Your total is *{ugx(order.total)}*.\n"
        "We'll confirm your order shortly.\n\n"
        f"Status: *{order.get_status_display()}*\n\nType *menu* anytime to order again."
    )


TEXT_HANDLERS = {
    "QUANTITY_INPUT": handle_quantity,
    "CHECKOUT_NAME": handle_name,
    "CHECKOUT_ADDRESS": handle_address,
}