from django.db import migrations


def seed_form_settings(apps, schema_editor):
    """Seed the initial form settings row."""
    FormSettings = apps.get_model("form_settings", "FormSettings")

    # Create the singleton settings row with default values
    FormSettings.objects.get_or_create(
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


def reverse_seed(apps, schema_editor):
    """Reverse the seed by deleting the settings row."""
    FormSettings = apps.get_model("form_settings", "FormSettings")
    FormSettings.objects.filter(id=1).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("form_settings", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_form_settings, reverse_seed),
    ]
