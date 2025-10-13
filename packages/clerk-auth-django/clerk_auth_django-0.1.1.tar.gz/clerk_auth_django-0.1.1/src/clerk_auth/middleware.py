"""Django middleware for Clerk authentication."""

from typing import Callable, Optional
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin
import jwt

from .authentication import verify_clerk_token
from .utils import (
    get_clerk_config,
    get_or_create_user_from_claims,
    attach_clerk_claims_to_user,
)


class ClerkAuthMiddleware(MiddlewareMixin):
    """
    Middleware that authenticates requests using Clerk JWT tokens.

    Attaches authenticated user to request.user if valid token present.
    Does not block requests - just attempts authentication.
    """

    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """Process request and attach user if token is valid."""
        # Extract token from Authorization header
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")

        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != "Bearer":
            return None

        token = parts[1]

        try:
            # Verify token and get claims
            claims = verify_clerk_token(token)

            # Get or create user
            update_on_auth = get_clerk_config("UPDATE_USER_ON_AUTH")
            user = get_or_create_user_from_claims(claims, update=update_on_auth)

            # Attach claims to user
            attach_clerk_claims_to_user(user, claims)

            # Attach user to request
            request.user = user

        except (jwt.PyJWTError, Exception):
            # Token invalid - don't block request, just don't attach user
            pass

        return None


class OrganizationContextMiddleware(MiddlewareMixin):
    """
    Middleware that adds organization context to requests for multi-tenancy.

    Reads organization ID from header and attaches to request.
    Validates that user is member of the specified organization.
    """

    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """Process request and attach organization context."""
        if not get_clerk_config("ENABLE_ORG_CONTEXT"):
            return None

        # Get organization header name from config
        org_header = get_clerk_config("ORG_HEADER")
        header_key = f"HTTP_{org_header.upper().replace('-', '_')}"

        # Extract organization ID from header
        org_id = request.META.get(header_key)

        if org_id:
            # Attach to request for easy access
            request.organization_id = org_id

            # Validate user is member of this organization if user is authenticated
            if hasattr(request, "user") and request.user.is_authenticated:
                user_org_id = getattr(request.user, "org_id", None)

                # If user has different org_id, they're not authorized for this org
                if user_org_id and user_org_id != org_id:
                    from django.http import JsonResponse
                    from rest_framework import status

                    return JsonResponse(
                        {"error": "User not authorized for this organization"},
                        status=status.HTTP_403_FORBIDDEN,
                    )

        return None
