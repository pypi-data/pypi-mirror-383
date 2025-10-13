"""Function decorators for Clerk authentication."""

from functools import wraps
from typing import Callable
from django.http import JsonResponse
from rest_framework import status


def require_auth(func: Callable) -> Callable:
    """
    Decorator that requires user to be authenticated.

    Usage:
        @require_auth
        def my_view(request):
            return Response({'user': request.user.clerk_id})
    """

    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user or not request.user.is_authenticated:
            return JsonResponse(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return func(request, *args, **kwargs)

    return wrapper


def require_role(role: str) -> Callable:
    """
    Decorator that requires user to have a specific organization role.

    Usage:
        @require_role('admin')
        def admin_view(request):
            return Response({'message': 'Admin access'})
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user or not request.user.is_authenticated:
                return JsonResponse(
                    {"error": "Authentication required"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            user_role = getattr(request.user, "org_role", None)
            if user_role != role:
                return JsonResponse(
                    {"error": f"Role '{role}' required"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            return func(request, *args, **kwargs)

        return wrapper

    return decorator


def require_permission(permission: str) -> Callable:
    """
    Decorator that requires user to have a specific permission.

    Usage:
        @require_permission('write:invoices')
        def create_invoice(request):
            return Response({'message': 'Invoice created'})
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user or not request.user.is_authenticated:
                return JsonResponse(
                    {"error": "Authentication required"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            user_permissions = getattr(request.user, "permissions", [])
            if permission not in user_permissions:
                return JsonResponse(
                    {"error": f"Permission '{permission}' required"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            return func(request, *args, **kwargs)

        return wrapper

    return decorator
