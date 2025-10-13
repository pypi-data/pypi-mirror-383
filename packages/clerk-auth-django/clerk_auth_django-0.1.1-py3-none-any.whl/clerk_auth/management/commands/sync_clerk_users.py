"""Management command to sync users from Clerk API."""

from django.core.management.base import BaseCommand
from clerk_auth.api_client import ClerkAPIClient
from clerk_auth.utils import get_clerk_config, get_user_model


class Command(BaseCommand):
    """Sync users from Clerk API to local database."""

    help = "Sync users from Clerk API to local database"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--limit",
            type=int,
            default=100,
            help="Number of users to fetch per batch (default: 100)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be synced without making changes",
        )

    def handle(self, *args, **options):
        """Execute command."""
        limit = options["limit"]
        dry_run = options["dry_run"]

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made"))

        # Initialize Clerk API client
        try:
            client = ClerkAPIClient()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to initialize Clerk API client: {e}"))
            return

        # Get user model
        User = get_user_model()
        field_mapping = get_clerk_config("USER_FIELD_MAPPING")

        # Fetch users from Clerk
        self.stdout.write("Fetching users from Clerk API...")

        offset = 0
        total_synced = 0
        total_created = 0
        total_updated = 0

        while True:
            try:
                users = client.list_users(limit=limit, offset=offset)

                if not users:
                    break

                for user_data in users:
                    clerk_id = user_data.get("id")
                    if not clerk_id:
                        continue

                    # Map fields from Clerk data
                    mapped_data = {}
                    for model_field, clerk_field in field_mapping.items():
                        if clerk_field in user_data:
                            mapped_data[model_field] = user_data[clerk_field]

                    if dry_run:
                        exists = User.objects.filter(pk=clerk_id).exists()
                        action = "Update" if exists else "Create"
                        self.stdout.write(f"  {action}: {clerk_id} - {mapped_data}")
                    else:
                        # Get or create user
                        user, created = User.objects.get_or_create(
                            clerk_id=clerk_id,
                            defaults=mapped_data,
                        )

                        if created:
                            total_created += 1
                            self.stdout.write(
                                self.style.SUCCESS(f"  Created user: {clerk_id}")
                            )
                        else:
                            # Update existing user
                            updated = False
                            for field, value in mapped_data.items():
                                if getattr(user, field) != value:
                                    setattr(user, field, value)
                                    updated = True

                            if updated:
                                user.save()
                                total_updated += 1
                                self.stdout.write(
                                    self.style.SUCCESS(f"  Updated user: {clerk_id}")
                                )

                    total_synced += 1

                offset += len(users)

                if len(users) < limit:
                    break

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error fetching users: {e}"))
                break

        # Summary
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f"\nDRY RUN: Would sync {total_synced} users")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nSync complete: {total_synced} users processed "
                    f"({total_created} created, {total_updated} updated)"
                )
            )
