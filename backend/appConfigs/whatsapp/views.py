# whatsapp/views.py
import json
import logging
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ProcessedMessage
from .handlers import handle_incoming_message

logger = logging.getLogger("whatsapp")


@method_decorator(csrf_exempt, name="dispatch")
class WhatsAppWebhookView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        """Meta's one-time verification handshake."""
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
            return HttpResponse(challenge)
        return HttpResponse("Verification failed", status=403)

    def post(self, request):
        """Receives every message/status event Meta sends."""
        payload = request.data
        logger.info("WhatsApp webhook payload: %s", json.dumps(payload))

        try:
            entry = payload["entry"][0]
            change = entry["changes"][0]["value"]
        except (KeyError, IndexError):
            # status updates, or a shape we don't handle yet — ack anyway so Meta stops retrying
            return Response(status=200)

        messages = change.get("messages")
        if not messages:
            # this was a delivery/read status update, not an incoming message
            return Response(status=200)

        contacts = change.get("contacts") or [{}]
        profile_name = contacts[0].get("profile", {}).get("name", "")

        for message in messages:
            _, created = ProcessedMessage.objects.get_or_create(message_id=message["id"])
            if not created:
                continue  # Meta retry, already handled

        from_number = message["from"]
        business_phone_id = change["metadata"]["phone_number_id"]
        text = message.get("text", {}).get("body", "")
        interactive = message.get("interactive", {})
        action_id = (
        interactive.get("button_reply", {}).get("id")
        or interactive.get("list_reply", {}).get("id")
        )

        try:
            handle_incoming_message(business_phone_id, from_number, text, action_id, profile_name)
        except Exception:
        # never let a handler bug turn into a non-200, or Meta will retry the same message
            logger.exception("Error handling message %s", message["id"])

        return Response(status=200)