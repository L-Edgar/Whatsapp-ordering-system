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

        for message in messages:
            message_id = message["id"]

            # idempotency: Meta retries on any non-200 or timeout — don't double-process
            if ProcessedMessage.objects.filter(message_id=message_id).exists():
                continue
            ProcessedMessage.objects.create(message_id=message_id)

            from_number = message["from"]
            business_phone_id = change["metadata"]["phone_number_id"]
            text = message.get("text", {}).get("body", "")
            button_reply = message.get("interactive", {}).get("button_reply", {}).get("id")
            list_reply = message.get("interactive", {}).get("list_reply", {}).get("id")

            logger.info(
                "Message from %s to business_phone_id=%s: text=%r button=%r list=%r",
                from_number, business_phone_id, text, button_reply, list_reply,
            )

            # Stage 5 will replace this stub with the real conversation dispatcher
            # handle_incoming_message(business_phone_id, from_number, text, button_reply or list_reply)

        return Response(status=200)