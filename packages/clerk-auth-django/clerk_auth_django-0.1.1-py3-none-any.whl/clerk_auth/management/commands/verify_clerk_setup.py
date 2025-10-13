"""Management command to verify Clerk configuration."""

from django.core.management.base import BaseCommand
from django.conf import settings
from clerk_auth.utils import get_clerk_config, get_user_model, fetch_clerk_public_keys


class Command(BaseCommand):
    """Verify Clerk authentication setup."""

    help = "Verify Clerk authentication configuration and connectivity"

    def handle(self, *args, **options):
        """Execute command."""
        self.stdout.write(self.style.HTTP_INFO("Verifying Clerk configuration...\n"))

        all_checks_passed = True

        # Check 1: CLERK_AUTH settings exist
        self.stdout.write("1. Checking CLERK_AUTH settings...")
        clerk_settings = getattr(settings, "CLERK_AUTH", None)
        if not clerk_settings:
            self.stdout.write(
                self.style.ERROR("  FAILED: CLERK_AUTH not found in settings")
            )
            all_checks_passed = False
        else:
            self.stdout.write(self.style.SUCCESS("  OK: CLERK_AUTH settings found"))

        # Check 2: SECRET_KEY configured
        self.stdout.write("\n2. Checking SECRET_KEY...")
        secret_key = get_clerk_config("SECRET_KEY")
        if not secret_key:
            self.stdout.write(
                self.style.ERROR("  FAILED: CLERK_AUTH['SECRET_KEY'] not configured")
            )
            all_checks_passed = False
        elif not secret_key.startswith("sk_"):
            self.stdout.write(
                self.style.ERROR(
                    "  FAILED: SECRET_KEY must start with 'sk_' (Clerk format)"
                )
            )
            all_checks_passed = False
        else:
            # Mask the key for security
            masked_key = f"{secret_key[:10]}...{secret_key[-4:]}"
            self.stdout.write(
                self.style.SUCCESS(f"  OK: SECRET_KEY configured ({masked_key})")
            )

        # Check 3: USER_MODEL configured
        self.stdout.write("\n3. Checking USER_MODEL...")
        try:
            User = get_user_model()
            model_name = f"{User._meta.app_label}.{User._meta.model_name}"
            self.stdout.write(
                self.style.SUCCESS(f"  OK: USER_MODEL configured ({model_name})")
            )

            # Check if model has clerk_id field
            if not hasattr(User, "clerk_id"):
                self.stdout.write(
                    self.style.WARNING(
                        "  WARNING: User model doesn't have 'clerk_id' field. "
                        "Make sure it inherits from ClerkUser."
                    )
                )
                all_checks_passed = False
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  FAILED: {e}"))
            all_checks_passed = False

        # Check 4: Connectivity to Clerk API
        self.stdout.write("\n4. Checking connectivity to Clerk API...")
        try:
            jwks = fetch_clerk_public_keys()
            num_keys = len(jwks.get("keys", []))
            self.stdout.write(
                self.style.SUCCESS(f"  OK: Connected to Clerk API ({num_keys} public keys)")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  FAILED: {e}"))
            all_checks_passed = False

        # Check 5: Optional settings
        self.stdout.write("\n5. Checking optional settings...")

        webhook_secret = get_clerk_config("WEBHOOK_SECRET")
        if webhook_secret:
            masked_secret = f"{webhook_secret[:10]}...{webhook_secret[-4:]}"
            self.stdout.write(
                self.style.SUCCESS(f"  Webhook secret: {masked_secret}")
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "  Webhook secret not configured (webhooks will not be verified)"
                )
            )

        cache_enabled = get_clerk_config("CACHE_PUBLIC_KEYS")
        self.stdout.write(f"  Public key caching: {'enabled' if cache_enabled else 'disabled'}")

        org_context = get_clerk_config("ENABLE_ORG_CONTEXT")
        self.stdout.write(f"  Organization context: {'enabled' if org_context else 'disabled'}")

        # Final summary
        self.stdout.write("\n" + "=" * 50)
        if all_checks_passed:
            self.stdout.write(
                self.style.SUCCESS("\nAll checks passed! Clerk setup is correct.")
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    "\nSome checks failed. Please fix the issues above."
                )
            )
