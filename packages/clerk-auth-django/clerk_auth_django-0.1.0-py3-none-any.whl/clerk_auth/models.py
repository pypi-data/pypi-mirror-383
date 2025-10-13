"""Django models for Clerk authentication."""

from django.db import models


class ClerkUser(models.Model):
    """
    Abstract base model for minimal user records with Clerk integration.

    This model stores ONLY app-specific data. Clerk is the source of truth for:
    - Authentication (email, password, name)
    - Organization roles and memberships
    - Public/private metadata

    The clerk_id is the primary key, enabling normal Django ForeignKey relationships
    while keeping Clerk as the authentication source.

    Usage:
        class User(ClerkUser):
            stripe_customer_id = models.CharField(max_length=255, null=True)
            subscription_tier = models.CharField(max_length=50, default='free')
            preferences = models.JSONField(default=dict)

        # Normal Django relationships work
        class Invoice(models.Model):
            user = models.ForeignKey(User, on_delete=models.CASCADE)
            amount = models.DecimalField(max_digits=10, decimal_places=2)

        # Query normally
        user.invoice_set.all()
        Invoice.objects.filter(user=request.user)
    """

    clerk_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="Clerk user ID (from JWT 'sub' claim)",
    )

    email = models.EmailField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Optional cached email from Clerk (for convenience)",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.email or self.clerk_id

    @property
    def is_authenticated(self) -> bool:
        """Always return True since Clerk handles authentication."""
        return True

    @property
    def is_anonymous(self) -> bool:
        """Always return False since this represents an authenticated user."""
        return False


class Organization(models.Model):
    """
    Optional model for storing local organization data.

    Note: This is NOT for organization auth/membership - Clerk handles that.
    Use this only if you need to store app-specific organization data locally.

    Organization membership and roles come from JWT claims, not this model.
    """

    clerk_org_id = models.CharField(
        max_length=255,
        unique=True,
        help_text="Clerk organization ID",
    )

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    # App-specific fields
    subscription_tier = models.CharField(max_length=50, default="free")
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
