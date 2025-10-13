"""Utility functions for Clerk authentication."""

from typing import Any, Dict, Optional
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
import requests


# Default configuration values
DEFAULTS = {
    "AUTO_CREATE_USER": True,
    "UPDATE_USER_ON_AUTH": False,
    "USER_FIELD_MAPPING": {},
    "ROLE_CLAIM": "org_role",
    "ORG_CLAIM": "org_id",
    "PERMISSIONS_CLAIM": "permissions",
    "METADATA_CLAIM": "public_metadata",
    "CACHE_PUBLIC_KEYS": True,
    "CACHE_TIMEOUT": 3600,
    "CACHE_KEY_PREFIX": "clerk_auth",
    "ENABLE_ORG_CONTEXT": True,
    "ORG_HEADER": "X-Organization-ID",
    "REQUIRED_CLAIMS": [],
    "ALLOWED_ALGORITHMS": ["RS256"],
    "WEBHOOK_TOLERANCE": 300,
}


def get_clerk_config(key: str, default: Any = None) -> Any:
    """Get Clerk configuration value with fallback to defaults."""
    clerk_settings = getattr(settings, "CLERK_AUTH", {})
    if default is None:
        default = DEFAULTS.get(key)
    return clerk_settings.get(key, default)


def validate_clerk_config() -> None:
    """Validate Clerk configuration on app startup."""
    clerk_settings = getattr(settings, "CLERK_AUTH", {})

    if not clerk_settings:
        raise ImproperlyConfigured("CLERK_AUTH settings must be defined in settings.py")

    if not clerk_settings.get("SECRET_KEY"):
        raise ImproperlyConfigured("CLERK_AUTH['SECRET_KEY'] is required")

    # Validate SECRET_KEY format
    secret_key = clerk_settings.get("SECRET_KEY", "")
    if not secret_key.startswith("sk_"):
        raise ImproperlyConfigured(
            "CLERK_AUTH['SECRET_KEY'] must start with 'sk_' (Clerk secret key format)"
        )


def get_clerk_jwks_url() -> str:
    """Get Clerk JWKS URL based on secret key."""
    secret_key = get_clerk_config("SECRET_KEY")
    if not secret_key:
        raise ImproperlyConfigured("CLERK_AUTH['SECRET_KEY'] is required")

    # Extract instance ID from secret key (format: sk_{env}_{instance_id}_...)
    parts = secret_key.split("_")
    if len(parts) < 3:
        raise ImproperlyConfigured("Invalid Clerk secret key format")

    # Build JWKS URL - Clerk provides JWKS at this endpoint
    return f"https://api.clerk.com/v1/jwks"


def fetch_clerk_public_keys() -> Dict[str, Any]:
    """Fetch Clerk's public keys from JWKS endpoint with caching."""
    cache_enabled = get_clerk_config("CACHE_PUBLIC_KEYS")
    cache_key = f"{get_clerk_config('CACHE_KEY_PREFIX')}_jwks"

    # Try cache first
    if cache_enabled:
        cached_jwks = cache.get(cache_key)
        if cached_jwks:
            return cached_jwks

    # Fetch from Clerk API
    secret_key = get_clerk_config("SECRET_KEY")
    headers = {"Authorization": f"Bearer {secret_key}"}

    try:
        response = requests.get(get_clerk_jwks_url(), headers=headers, timeout=10)
        response.raise_for_status()
        jwks = response.json()

        # Cache the result
        if cache_enabled:
            cache_timeout = get_clerk_config("CACHE_TIMEOUT")
            cache.set(cache_key, jwks, cache_timeout)

        return jwks
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch Clerk public keys: {str(e)}") from e


def get_user_model():
    """Get the configured user model."""
    from django.apps import apps

    user_model_path = get_clerk_config("USER_MODEL")
    if not user_model_path:
        raise ImproperlyConfigured("CLERK_AUTH['USER_MODEL'] is required")

    try:
        return apps.get_model(user_model_path)
    except (LookupError, ValueError) as e:
        raise ImproperlyConfigured(
            f"CLERK_AUTH['USER_MODEL'] refers to model '{user_model_path}' "
            f"that has not been installed or is invalid"
        ) from e


def get_or_create_user_from_claims(claims: Dict[str, Any], update: bool = False):
    """Get or create user from JWT claims."""
    User = get_user_model()
    clerk_id = claims.get("sub")

    if not clerk_id:
        raise ValueError("JWT claims missing 'sub' (clerk_id)")

    # Prepare user data from field mapping
    user_data = {}
    field_mapping = get_clerk_config("USER_FIELD_MAPPING")

    for model_field, claim_field in field_mapping.items():
        if claim_field in claims:
            user_data[model_field] = claims[claim_field]

    # Get or create user
    auto_create = get_clerk_config("AUTO_CREATE_USER")

    try:
        user = User.objects.get(pk=clerk_id)
        # Update user fields if configured
        if update and user_data:
            for field, value in user_data.items():
                setattr(user, field, value)
            user.save()
    except User.DoesNotExist:
        if not auto_create:
            raise ValueError(f"User with clerk_id {clerk_id} does not exist")

        # Create new user
        user = User.objects.create(clerk_id=clerk_id, **user_data)

    return user


def attach_clerk_claims_to_user(user, claims: Dict[str, Any]) -> None:
    """Attach JWT claims to user object for easy access."""
    user.clerk_claims = claims
    user.org_role = claims.get(get_clerk_config("ROLE_CLAIM"))
    user.org_id = claims.get(get_clerk_config("ORG_CLAIM"))
    user.permissions = claims.get(get_clerk_config("PERMISSIONS_CLAIM"), [])
    user.metadata = claims.get(get_clerk_config("METADATA_CLAIM"), {})
