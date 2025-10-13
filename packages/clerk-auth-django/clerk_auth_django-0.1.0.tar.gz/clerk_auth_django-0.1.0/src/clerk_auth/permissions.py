"""DRF permission classes for Clerk authentication."""

from typing import List
from rest_framework import permissions


class HasRole(permissions.BasePermission):
    """
    Permission class that checks if user has a specific organization role.

    Usage:
        permission_classes = [HasRole('admin')]
    """

    def __init__(self, role: str):
        """Initialize with required role."""
        self.required_role = role

    def has_permission(self, request, view):
        """Check if user has the required role."""
        if not request.user or not request.user.is_authenticated:
            return False

        user_role = getattr(request.user, "org_role", None)
        return user_role == self.required_role


class HasAnyRole(permissions.BasePermission):
    """
    Permission class that checks if user has any of the specified roles.

    Usage:
        permission_classes = [HasAnyRole('admin', 'editor')]
    """

    def __init__(self, *roles: str):
        """Initialize with list of allowed roles."""
        self.allowed_roles = roles

    def has_permission(self, request, view):
        """Check if user has any of the allowed roles."""
        if not request.user or not request.user.is_authenticated:
            return False

        user_role = getattr(request.user, "org_role", None)
        return user_role in self.allowed_roles


class HasPermission(permissions.BasePermission):
    """
    Permission class that checks if user has a specific permission string.

    Usage:
        permission_classes = [HasPermission('read:invoices')]
    """

    def __init__(self, permission: str):
        """Initialize with required permission."""
        self.required_permission = permission

    def has_permission(self, request, view):
        """Check if user has the required permission."""
        if not request.user or not request.user.is_authenticated:
            return False

        user_permissions = getattr(request.user, "permissions", [])
        return self.required_permission in user_permissions


class HasAllPermissions(permissions.BasePermission):
    """
    Permission class that checks if user has all specified permissions.

    Usage:
        permission_classes = [HasAllPermissions('read:invoices', 'write:invoices')]
    """

    def __init__(self, *perms: str):
        """Initialize with list of required permissions."""
        self.required_permissions = perms

    def has_permission(self, request, view):
        """Check if user has all required permissions."""
        if not request.user or not request.user.is_authenticated:
            return False

        user_permissions = getattr(request.user, "permissions", [])
        return all(perm in user_permissions for perm in self.required_permissions)


class IsOrgMember(permissions.BasePermission):
    """
    Permission class that checks if user is a member of any organization.

    Usage:
        permission_classes = [IsOrgMember]
    """

    def has_permission(self, request, view):
        """Check if user has an organization ID."""
        if not request.user or not request.user.is_authenticated:
            return False

        org_id = getattr(request.user, "org_id", None)
        return org_id is not None


class IsOrgAdmin(permissions.BasePermission):
    """
    Permission class that checks if user has admin role in their organization.

    Shortcut for HasRole('admin').

    Usage:
        permission_classes = [IsOrgAdmin]
    """

    def has_permission(self, request, view):
        """Check if user has admin role."""
        if not request.user or not request.user.is_authenticated:
            return False

        user_role = getattr(request.user, "org_role", None)
        return user_role == "admin"
