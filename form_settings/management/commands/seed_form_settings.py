"""
Management command to seed initial form settings.
This replaces the seeding logic previously in migrations.
"""
from django.core.management.base import BaseCommand
from form_settings.models import FormSettings


class Command(BaseCommand):
    help = "Seed initial form settings (singleton row)"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding form settings...")

        settings, created = FormSettings.objects.get_or_create(
            id=1,
            defaults={
                "membership_fee": 1450.00,
                "gcash_accounts": [],
                "bank_accounts": [],
                "cash_payment": {
                    "address": "",
                    "building": "",
                    "office": "",
                    "openDays": [],
                    "openHours": "",
                },
                "success_message": "",
            },
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS("Form settings created successfully!")
            )
        else:
            self.stdout.write(
                self.style.WARNING("Form settings already exist, skipping seed.")
            )
