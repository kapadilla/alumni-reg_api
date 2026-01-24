"""
Management command to set up the entire database.
Runs all migrations and seeds all required initial data.
Use this for fresh deployments.
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Set up the database: run migrations and seed all initial data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-migrations",
            action="store_true",
            help="Skip running migrations (useful if already applied)",
        )
        parser.add_argument(
            "--skip-seeds",
            action="store_true",
            help="Skip seeding data (useful if already seeded)",
        )
        parser.add_argument(
            "--with-mock-data",
            action="store_true",
            help="Also generate mock test data (NOT for production)",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("=" * 60))
        self.stdout.write(self.style.NOTICE(" Alumni Registration API - Database Setup"))
        self.stdout.write(self.style.NOTICE("=" * 60))

        # Step 1: Run migrations
        if not options["skip_migrations"]:
            self.stdout.write("\n📦 Running migrations...")
            try:
                call_command("migrate", verbosity=1)
                self.stdout.write(self.style.SUCCESS("✅ Migrations complete"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Migration failed: {e}"))
                return
        else:
            self.stdout.write(self.style.WARNING("⏭️  Skipping migrations"))

        # Step 2: Seed form settings
        if not options["skip_seeds"]:
            self.stdout.write("\n🌱 Seeding form settings...")
            try:
                call_command("seed_form_settings")
                self.stdout.write(self.style.SUCCESS("✅ Form settings seeded"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Seeding failed: {e}"))
                return
        else:
            self.stdout.write(self.style.WARNING("⏭️  Skipping seeds"))

        # Step 3: Optional mock data
        if options["with_mock_data"]:
            self.stdout.write("\n🎭 Generating mock data (for testing only)...")
            try:
                call_command("seed_mock_data")
                self.stdout.write(self.style.SUCCESS("✅ Mock data generated"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Mock data generation failed: {e}"))
                return

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("🎉 Database setup complete!"))
        self.stdout.write("=" * 60)

        self.stdout.write("\n📋 Next steps:")
        self.stdout.write("   1. Create a superuser: python manage.py createsuperuser")
        self.stdout.write("   2. Start the server: python manage.py runserver")
        self.stdout.write("")
