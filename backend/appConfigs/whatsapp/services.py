import requests
from django.conf import settings

WHATSAPP_API_VERSION = "v21.0"


def send_text_message(phone_number_id, access_token, to, body):
    url = f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{phone_number_id}/messages"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body},
    }
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    if not response.ok:
        # don't swallow this — a failed send should be visible in logs during dev
        import logging
        logging.getLogger("whatsapp").error("Send failed: %s %s", response.status_code, response.text)
    return response


def send_button_message(phone_number_id, access_token, to, body, buttons):
    """buttons: list of {"id": "shop", "title": "Shop"} dicts, max 3."""
    url = f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{phone_number_id}/messages"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": b["id"], "title": b["title"]}} for b in buttons
                ]
            },
        },
    }
    return requests.post(url, headers=headers, json=payload, timeout=10)