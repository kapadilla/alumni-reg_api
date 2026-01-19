import re
from rest_framework import serializers
from .models import FormSettings


# ============================================
# NESTED SERIALIZERS FOR PAYMENT ACCOUNTS
# ============================================


class GcashAccountSerializer(serializers.Serializer):
    """Serializer for GCash account validation."""

    name = serializers.CharField(max_length=255)
    number = serializers.CharField(max_length=11, min_length=11)

    def validate_number(self, value):
        """Validate GCash number format: 11 digits starting with 09."""
        if not re.match(r"^09[0-9]{9}$", value):
            raise serializers.ValidationError(
                "Invalid GCash number format. Must be 11 digits starting with 09."
            )
        return value


class BankAccountSerializer(serializers.Serializer):
    """Serializer for bank account validation."""

    # snake_case: djangorestframework-camel-case converts incoming camelCase to snake_case
    bank_name = serializers.CharField(max_length=255)
    account_name = serializers.CharField(max_length=255)
    account_number = serializers.CharField(max_length=255)


class CashPaymentSerializer(serializers.Serializer):
    """Serializer for cash payment details validation."""

    VALID_DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

    address = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    building = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    office = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    # snake_case: djangorestframework-camel-case converts incoming camelCase to snake_case
    open_days = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )
    open_hours = serializers.CharField(
        max_length=100, required=False, allow_blank=True, default=""
    )

    def validate_open_days(self, value):
        """Validate that openDays contains only valid day codes."""
        invalid_days = [day for day in value if day not in self.VALID_DAYS]
        if invalid_days:
            raise serializers.ValidationError(
                f"Invalid day(s): {', '.join(invalid_days)}. "
                f"Valid values are: {', '.join(self.VALID_DAYS)}"
            )
        return value


class PaymentSettingsSerializer(serializers.Serializer):
    """Serializer for the payment_settings nested object."""

    # snake_case: djangorestframework-camel-case converts incoming camelCase to snake_case
    gcash_accounts = GcashAccountSerializer(many=True, required=False, default=list)
    bank_accounts = BankAccountSerializer(many=True, required=False, default=list)
    cash_payment = CashPaymentSerializer(required=False)

    def to_internal_value(self, data):
        # Provide defaults if not present
        if "cash_payment" not in data or data["cash_payment"] is None:
            data["cash_payment"] = {
                "address": "",
                "building": "",
                "office": "",
                "open_days": [],
                "open_hours": "",
            }
        return super().to_internal_value(data)


# ============================================
# ADMIN SERIALIZERS
# ============================================


class AdminFormSettingsSerializer(serializers.Serializer):
    """
    Serializer for admin form settings endpoint.
    Handles both input validation and output formatting.

    Note: Field names are snake_case because djangorestframework-camel-case
    automatically converts incoming camelCase JSON to snake_case.
    """

    # snake_case: djangorestframework-camel-case converts incoming camelCase to snake_case
    membership_fee = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=0
    )
    payment_settings = PaymentSettingsSerializer()
    success_message = serializers.CharField(
        max_length=500, required=False, allow_blank=True, default=""
    )

    def validate_success_message(self, value):
        """Ensure success message doesn't exceed 500 characters."""
        if len(value) > 500:
            raise serializers.ValidationError(
                "Success message must not exceed 500 characters"
            )
        return value

    def to_representation(self, instance):
        """Convert FormSettings model to API response format."""
        # Handle cash_payment being None or empty
        cash_payment = instance.cash_payment or {
            "address": "",
            "building": "",
            "office": "",
            "open_days": [],
            "open_hours": "",
        }

        # Use snake_case - the CamelCaseJSONRenderer will convert to camelCase in response
        return {
            "membership_fee": float(instance.membership_fee),
            "payment_settings": {
                "gcash_accounts": instance.gcash_accounts or [],
                "bank_accounts": instance.bank_accounts or [],
                "cash_payment": cash_payment,
            },
            "success_message": instance.success_message or "",
        }


class AdminFormSettingsResponseSerializer(serializers.Serializer):
    """Serializer for the full admin GET response including metadata."""

    def to_representation(self, instance):
        settings_data = AdminFormSettingsSerializer().to_representation(instance)

        last_updated = None
        if instance.updated_by:
            last_updated = {
                "at": instance.updated_at.isoformat() if instance.updated_at else None,
                "by": {
                    "id": instance.updated_by.id,
                    "name": f"{instance.updated_by.first_name} {instance.updated_by.last_name}".strip()
                    or instance.updated_by.email,
                    "email": instance.updated_by.email,
                },
            }
        elif instance.updated_at:
            last_updated = {"at": instance.updated_at.isoformat(), "by": None}

        return {"settings": settings_data, "last_updated": last_updated}


# ============================================
# PUBLIC SERIALIZER
# ============================================


class PublicFormSettingsSerializer(serializers.Serializer):
    """
    Serializer for public form settings endpoint.
    Returns only the information needed for the registration form.
    Does NOT include admin details or modification history.
    """

    def to_representation(self, instance):
        # Handle cash_payment being None or empty
        cash_payment = instance.cash_payment or {
            "address": "",
            "building": "",
            "office": "",
            "open_days": [],
            "open_hours": "",
        }

        # Use snake_case - the CamelCaseJSONRenderer will convert to camelCase in response
        return {
            "membership_fee": float(instance.membership_fee),
            "payment_methods": {
                "gcash": {"accounts": instance.gcash_accounts or []},
                "bank": {"accounts": instance.bank_accounts or []},
                "cash": cash_payment,
            },
            "success_message": instance.success_message or "",
        }
