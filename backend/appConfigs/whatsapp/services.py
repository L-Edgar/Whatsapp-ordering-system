import requests
from django.conf import settings
import logging, requests

WHATSAPP_API_VERSION = "v21.0"
logger = logging.getLogger("whatsapp")

def _post(phone_number_id, access_token, payload):
    url = f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{phone_number_id}/messages"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
    except requests.exceptions.RequestException as exc:
        logger.error("WhatsApp send failed (network): %s", exc)
        return None

    if not response.ok:
        try:
            code = response.json().get("error", {}).get("code")
        except ValueError:
            code = None
        if code == 190:
            logger.error("WhatsApp access token expired or invalid. Regenerate it and update WhatsAppConfiguration.")
        else:
            logger.error("WhatsApp send failed: %s %s", response.status_code, response.text)
    return response


def send_text_message(phone_number_id, access_token, to, body):
    return _post(phone_number_id, access_token, {
        "messaging_product": "whatsapp",
        "to": to.lstrip("+"),
        "type": "text",
        "text": {"body": body},
    })


def send_button_message(phone_number_id, access_token, to, body, buttons):
    """buttons: list of {"id": "shop", "title": "Shop"} dicts, max 3."""
    return _post(phone_number_id, access_token, {
        "messaging_product": "whatsapp",
        "to": to.lstrip("+"),
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
    })
    
def send_list_message(phone_number_id, access_token, to, body, button_text, rows, section_title="Options"):
    """rows: list of {"id": "cat:4", "title": "Vegetables", "description": "optional"}, max 10."""
    clean_rows = []
    for r in rows[:10]:
        row = {"id": r["id"], "title": r["title"][:24]}
        if r.get("description"):
            row["description"] = r["description"][:72]
        clean_rows.append(row)

    return _post(phone_number_id, access_token, {
        "messaging_product": "whatsapp",
        "to": to.lstrip("+"),
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": body[:1024]},
            "action": {
                "button": button_text[:20],
                "sections": [{"title": section_title[:24], "rows": clean_rows}],
            },
        },
    })