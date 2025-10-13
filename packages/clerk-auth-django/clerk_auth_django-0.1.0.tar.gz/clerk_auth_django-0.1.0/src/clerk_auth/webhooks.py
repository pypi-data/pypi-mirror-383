"""Webhook handlers for Clerk events."""

import hashlib
import hmac
import json
import time
from typing import Any, Dict
from django.http import HttpRequest, JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import status

from .utils import get_clerk_config, get_user_model


def verify_webhook_signature(payload: bytes, headers: Dict[str, str]) -> bool:
    """
    Verify Clerk webhook signature using HMAC-SHA256.

    Args:
        payload: Raw request body as bytes
        headers: Request headers dict

    Returns:
        True if signature is valid, False otherwise
    """
    webhook_secret = get_clerk_config("WEBHOOK_SECRET")
    if not webhook_secret:
        # If no secret configured, accept all webhooks (dev mode)
        return True

    # Extract signature and timestamp from headers
    svix_id = headers.get("svix-id")
    svix_timestamp = headers.get("svix-timestamp")
    svix_signature = headers.get("svix-signature")

    if not all([svix_id, svix_timestamp, svix_signature]):
        return False

    # Check timestamp to prevent replay attacks
    try:
        webhook_tolerance = get_clerk_config("WEBHOOK_TOLERANCE")
        timestamp = int(svix_timestamp)
        current_time = int(time.time())

        if abs(current_time - timestamp) > webhook_tolerance:
            return False
    except (ValueError, TypeError):
        return False

    # Construct signed content (Svix format)
    signed_content = f"{svix_id}.{svix_timestamp}.{payload.decode('utf-8')}"

    # Compute HMAC signature
    expected_signature = hmac.new(
        webhook_secret.encode("utf-8"),
        signed_content.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    # Compare signatures (extract first signature if multiple)
    provided_signature = svix_signature.split(",")[0].split("=")[-1]

    return hmac.compare_digest(expected_signature, provided_signature)


class ClerkWebhookHandler:
    """
    Base webhook handler for Clerk events.

    Subclass this and override event methods to handle specific events.
    """

    def handle_user_created(self, event_data: Dict[str, Any]) -> None:
        """Handle user.created event."""
        User = get_user_model()
        user_data = event_data.get("data", {})
        clerk_id = user_data.get("id")

        if not clerk_id:
            return

        # Get field mapping
        field_mapping = get_clerk_config("USER_FIELD_MAPPING")
        mapped_data = {}

        for model_field, clerk_field in field_mapping.items():
            if clerk_field in user_data:
                mapped_data[model_field] = user_data[clerk_field]

        # Create user if doesn't exist
        User.objects.get_or_create(clerk_id=clerk_id, defaults=mapped_data)

    def handle_user_updated(self, event_data: Dict[str, Any]) -> None:
        """Handle user.updated event."""
        User = get_user_model()
        user_data = event_data.get("data", {})
        clerk_id = user_data.get("id")

        if not clerk_id:
            return

        try:
            user = User.objects.get(pk=clerk_id)

            # Update mapped fields
            field_mapping = get_clerk_config("USER_FIELD_MAPPING")
            updated = False

            for model_field, clerk_field in field_mapping.items():
                if clerk_field in user_data:
                    setattr(user, model_field, user_data[clerk_field])
                    updated = True

            if updated:
                user.save()
        except User.DoesNotExist:
            # User doesn't exist locally, create it
            self.handle_user_created(event_data)

    def handle_user_deleted(self, event_data: Dict[str, Any]) -> None:
        """Handle user.deleted event."""
        User = get_user_model()
        user_data = event_data.get("data", {})
        clerk_id = user_data.get("id")

        if not clerk_id:
            return

        try:
            user = User.objects.get(pk=clerk_id)
            user.delete()
        except User.DoesNotExist:
            pass

    def handle_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Route event to appropriate handler method.

        Override this to handle custom events.
        """
        handlers = {
            "user.created": self.handle_user_created,
            "user.updated": self.handle_user_updated,
            "user.deleted": self.handle_user_deleted,
        }

        handler = handlers.get(event_type)
        if handler:
            handler(event_data)


@method_decorator(csrf_exempt, name="dispatch")
class ClerkWebhookView(View):
    """
    Django view for receiving Clerk webhooks.

    Usage:
        # urls.py
        urlpatterns = [
            path('webhooks/clerk/', ClerkWebhookView.as_view()),
        ]
    """

    handler_class = ClerkWebhookHandler

    def post(self, request: HttpRequest) -> JsonResponse:
        """Handle incoming webhook POST request."""
        # Get raw body for signature verification
        payload = request.body

        # Extract headers
        headers = {
            "svix-id": request.META.get("HTTP_SVIX_ID", ""),
            "svix-timestamp": request.META.get("HTTP_SVIX_TIMESTAMP", ""),
            "svix-signature": request.META.get("HTTP_SVIX_SIGNATURE", ""),
        }

        # Verify signature
        if not verify_webhook_signature(payload, headers):
            return JsonResponse(
                {"error": "Invalid webhook signature"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Parse event data
        try:
            event = json.loads(payload)
        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON payload"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Extract event type and data
        event_type = event.get("type")
        event_data = event.get("data")

        if not event_type:
            return JsonResponse(
                {"error": "Missing event type"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Handle event
        try:
            handler = self.handler_class()
            handler.handle_event(event_type, event)
        except Exception as e:
            return JsonResponse(
                {"error": f"Failed to process webhook: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return JsonResponse({"success": True}, status=status.HTTP_200_OK)
