"""
Clerk Auth Django - Django REST Framework authentication library with Clerk integration.
"""

__version__ = "0.1.0"

__all__ = [
    "ClerkAuthentication",
    "ClerkJWTBackend",
    "verify_clerk_token",
    "HasRole",
    "HasAnyRole",
    "HasPermission",
    "HasAllPermissions",
    "IsOrgMember",
    "IsOrgAdmin",
    "require_auth",
    "require_role",
    "require_permission",
    "ClerkUser",
]


def __getattr__(name):
    """Lazy import to avoid Django AppRegistryNotReady errors."""
    if name == "ClerkAuthentication":
        from .authentication import ClerkAuthentication
        return ClerkAuthentication
    elif name == "ClerkJWTBackend":
        from .authentication import ClerkJWTBackend
        return ClerkJWTBackend
    elif name == "verify_clerk_token":
        from .authentication import verify_clerk_token
        return verify_clerk_token
    elif name == "HasRole":
        from .permissions import HasRole
        return HasRole
    elif name == "HasAnyRole":
        from .permissions import HasAnyRole
        return HasAnyRole
    elif name == "HasPermission":
        from .permissions import HasPermission
        return HasPermission
    elif name == "HasAllPermissions":
        from .permissions import HasAllPermissions
        return HasAllPermissions
    elif name == "IsOrgMember":
        from .permissions import IsOrgMember
        return IsOrgMember
    elif name == "IsOrgAdmin":
        from .permissions import IsOrgAdmin
        return IsOrgAdmin
    elif name == "require_auth":
        from .decorators import require_auth
        return require_auth
    elif name == "require_role":
        from .decorators import require_role
        return require_role
    elif name == "require_permission":
        from .decorators import require_permission
        return require_permission
    elif name == "ClerkUser":
        from .models import ClerkUser
        return ClerkUser
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
