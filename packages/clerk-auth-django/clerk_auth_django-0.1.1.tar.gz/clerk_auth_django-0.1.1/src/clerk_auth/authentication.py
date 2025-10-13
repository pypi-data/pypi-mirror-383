"""Clerk authentication classes for Django and DRF."""

from typing import Any, Dict, Optional, Tuple
import jwt
from jwt import PyJWKClient
from django.contrib.auth.backends import BaseBackend
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

from .utils import (
    get_clerk_config,
    fetch_clerk_public_keys,
    get_user_model,
    get_or_create_user_from_claims,
    attach_clerk_claims_to_user,
)


def verify_clerk_token(token: str) -> Dict[str, Any]:
    """
    Verify Clerk JWT token and return decoded claims.

    Args:
        token: JWT token string

    Returns:
        Dict containing JWT claims

    Raises:
        jwt.PyJWTError: If token is invalid
    """
    try:
        # Fetch JWKS (public keys) from Clerk
        jwks = fetch_clerk_public_keys()

        # Decode JWT header to get key ID
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        if not kid:
            raise jwt.InvalidTokenError("Token header missing 'kid' (key ID)")

        # Find the matching public key
        public_key = None
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
                break

        if not public_key:
            raise jwt.InvalidTokenError(f"Public key not found for kid: {kid}")

        # Verify and decode token
        allowed_algorithms = get_clerk_config("ALLOWED_ALGORITHMS")
        claims = jwt.decode(
            token,
            public_key,
            algorithms=allowed_algorithms,
            options={"verify_signature": True, "verify_exp": True},
        )

        # Validate required claims
        required_claims = get_clerk_config("REQUIRED_CLAIMS")
        for claim in required_claims:
            if claim not in claims:
                raise jwt.InvalidTokenError(f"Token missing required claim: {claim}")

        return claims

    except jwt.ExpiredSignatureError as e:
        raise jwt.ExpiredSignatureError("Token has expired") from e
    except jwt.InvalidTokenError as e:
        raise jwt.InvalidTokenError(f"Invalid token: {str(e)}") from e
    except Exception as e:
        raise jwt.PyJWTError(f"Token verification failed: {str(e)}") from e


class ClerkAuthentication(authentication.BaseAuthentication):
    """
    DRF authentication class for Clerk JWT tokens.

    Extracts JWT from Authorization header, verifies it, and gets/creates user.
    Attaches Clerk claims to the user object for access in views.
    """

    keyword = "Bearer"

    def authenticate(self, request) -> Optional[Tuple[Any, None]]:
        """
        Authenticate the request and return (user, None).

        Returns None if no auth header present (allows other auth classes to try).
        Raises AuthenticationFailed if token is invalid.
        """
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")

        if not auth_header:
            return None

        # Parse Authorization header
        parts = auth_header.split()

        if len(parts) != 2:
            raise AuthenticationFailed("Invalid Authorization header format")

        if parts[0] != self.keyword:
            return None

        token = parts[1]

        # Verify token and get claims
        try:
            claims = verify_clerk_token(token)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationFailed(f"Invalid token: {str(e)}")
        except Exception as e:
            raise AuthenticationFailed(f"Authentication failed: {str(e)}")

        # Get or create user from claims
        try:
            update_on_auth = get_clerk_config("UPDATE_USER_ON_AUTH")
            user = get_or_create_user_from_claims(claims, update=update_on_auth)
        except Exception as e:
            raise AuthenticationFailed(f"Failed to get/create user: {str(e)}")

        # Attach Clerk claims to user object
        attach_clerk_claims_to_user(user, claims)

        return (user, None)

    def authenticate_header(self, request) -> str:
        """Return WWW-Authenticate header value for 401 responses."""
        return f'{self.keyword} realm="api"'


class ClerkJWTBackend(BaseBackend):
    """
    Django authentication backend for Clerk JWT tokens.

    This allows using Clerk authentication with Django's auth system,
    not just DRF views.
    """

    def authenticate(
        self, request=None, token: Optional[str] = None, **kwargs
    ) -> Optional[Any]:
        """
        Authenticate using Clerk JWT token.

        Args:
            request: Django request object (optional)
            token: JWT token string (required)

        Returns:
            User instance if authentication succeeds, None otherwise
        """
        if not token:
            # Try to extract from request if provided
            if request:
                auth_header = request.META.get("HTTP_AUTHORIZATION", "")
                parts = auth_header.split()
                if len(parts) == 2 and parts[0] == "Bearer":
                    token = parts[1]

        if not token:
            return None

        try:
            # Verify token
            claims = verify_clerk_token(token)

            # Get or create user
            update_on_auth = get_clerk_config("UPDATE_USER_ON_AUTH")
            user = get_or_create_user_from_claims(claims, update=update_on_auth)

            # Attach claims
            attach_clerk_claims_to_user(user, claims)

            return user
        except Exception:
            # Silent failure - let other backends try
            return None

    def get_user(self, user_id):
        """Get user by primary key (required by Django auth backend interface)."""
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
