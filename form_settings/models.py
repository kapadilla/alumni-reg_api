from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class FormSettings(models.Model):
    """
    Singleton model for registration form settings.
    Stores membership fee, payment method details, and success message.
    Uses JSON fields for flexible payment account storage.
    """

    id = models.IntegerField(primary_key=True, default=1)

    # Membership fee
    membership_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1450.00,
        validators=[MinValueValidator(0)],
    )

    # Payment accounts stored as JSON arrays
    gcash_accounts = models.JSONField(
        default=list,
        blank=True,
        help_text='List of GCash accounts: [{"name": "...", "number": "09XXXXXXXXX"}]',
    )

    bank_accounts = models.JSONField(
        default=list,
        blank=True,
        help_text='List of bank accounts: [{"bankName": "...", "accountName": "...", "accountNumber": "..."}]',
    )

    # Cash payment details stored as JSON object
    cash_payment = models.JSONField(
        default=dict,
        blank=True,
        help_text='Cash payment details: {"address": "", "building": "", "office": "", "openDays": [], "openHours": ""}',
    )

    # Success page message
    success_message = models.CharField(max_length=500, blank=True, default="")

    # Audit fields
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="form_settings_updates",
    )

    class Meta:
        db_table = "form_settings"
        verbose_name = "Form Settings"
        verbose_name_plural = "Form Settings"

    def __str__(self):
        return f"Form Settings (Last updated: {self.updated_at})"

    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton pattern)
        self.id = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """Get or create the singleton settings instance."""
        settings, _ = cls.objects.get_or_create(id=1)
        return settings

    def get_default_cash_payment(self):
        """Return default cash payment structure."""
        return {
            "address": "",
            "building": "",
            "office": "",
            "openDays": [],
            "openHours": "",
        }


class FormSettingsHistory(models.Model):
    """
    Track detailed changes to form settings for audit purposes.
    Stores JSON diff of what changed.
    """

    admin = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="form_settings_changes"
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    changes = models.JSONField(help_text="JSON object containing the changes made")

    class Meta:
        db_table = "form_settings_history"
        ordering = ["-changed_at"]
        verbose_name = "Form Settings History"
        verbose_name_plural = "Form Settings History"

    def __str__(self):
        return f"Settings change by {self.admin.email} at {self.changed_at}"
