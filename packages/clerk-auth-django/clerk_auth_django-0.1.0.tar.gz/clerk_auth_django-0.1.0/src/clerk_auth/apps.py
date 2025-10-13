from django.apps import AppConfig


class ClerkAuthConfig(AppConfig):
    """Django app configuration for clerk_auth."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "clerk_auth"
    verbose_name = "Clerk Authentication"

    def ready(self) -> None:
        """Run when Django starts - validate configuration."""
        from .utils import validate_clerk_config

        # Validate Clerk configuration on startup
        validate_clerk_config()
