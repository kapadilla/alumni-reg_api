from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import FormSettings, FormSettingsHistory
from .serializers import (
    AdminFormSettingsSerializer,
    AdminFormSettingsResponseSerializer,
    PublicFormSettingsSerializer,
)
from accounts.models import AdminActivityLog


def generate_change_notes(old_data, new_data):
    """
    Generate human-readable notes about what changed.
    Returns a string summarizing the changes.
    """
    notes = []

    # Check membership fee change
    if old_data.get("membership_fee") != new_data.get("membership_fee"):
        old_fee = old_data.get("membership_fee", 0)
        new_fee = new_data.get("membership_fee", 0)
        notes.append(
            f"Changed membership fee from Php {old_fee:,.2f} to Php {new_fee:,.2f}"
        )

    old_payment = old_data.get("payment_settings", {})
    new_payment = new_data.get("payment_settings", {})

    # Check GCash accounts changes
    old_gcash = old_payment.get("gcash_accounts", [])
    new_gcash = new_payment.get("gcash_accounts", [])
    if old_gcash != new_gcash:
        old_count = len(old_gcash)
        new_count = len(new_gcash)
        if new_count > old_count:
            notes.append(f"Added {new_count - old_count} GCash account(s)")
        elif new_count < old_count:
            notes.append(f"Removed {old_count - new_count} GCash account(s)")
        else:
            notes.append("Modified GCash account(s)")

    # Check bank accounts changes
    old_bank = old_payment.get("bank_accounts", [])
    new_bank = new_payment.get("bank_accounts", [])
    if old_bank != new_bank:
        old_count = len(old_bank)
        new_count = len(new_bank)
        if new_count > old_count:
            notes.append(f"Added {new_count - old_count} bank account(s)")
        elif new_count < old_count:
            notes.append(f"Removed {old_count - new_count} bank account(s)")
        else:
            notes.append("Modified bank account(s)")

    # Check cash payment changes
    old_cash = old_payment.get("cash_payment", {})
    new_cash = new_payment.get("cash_payment", {})
    if old_cash != new_cash:
        changed_fields = []
        for field in ["address", "building", "office", "open_days", "open_hours"]:
            if old_cash.get(field) != new_cash.get(field):
                changed_fields.append(field)
        if changed_fields:
            notes.append(f"Modified cash payment details: {', '.join(changed_fields)}")

    # Check success message change
    if old_data.get("success_message") != new_data.get("success_message"):
        notes.append("Updated success page message")

    return ". ".join(notes) + "." if notes else "No changes detected."


def build_changes_json(old_data, new_data):
    """
    Build detailed JSON structure of changes for FormSettingsHistory.
    """
    changes = {}

    # Membership fee
    if old_data.get("membership_fee") != new_data.get("membership_fee"):
        changes["membership_fee"] = {
            "from": old_data.get("membership_fee"),
            "to": new_data.get("membership_fee"),
        }

    old_payment = old_data.get("payment_settings", {})
    new_payment = new_data.get("payment_settings", {})

    # GCash accounts
    old_gcash = old_payment.get("gcash_accounts", [])
    new_gcash = new_payment.get("gcash_accounts", [])
    if old_gcash != new_gcash:
        # Simple diff - track added/removed by comparing lists
        old_numbers = {acc.get("number") for acc in old_gcash}
        new_numbers = {acc.get("number") for acc in new_gcash}

        added = [acc for acc in new_gcash if acc.get("number") not in old_numbers]
        removed = [acc for acc in old_gcash if acc.get("number") not in new_numbers]

        changes["gcash_accounts"] = {
            "added": added,
            "removed": removed,
            "modified": [],  # Simplified - would need more logic for true modifications
        }

    # Bank accounts
    old_bank = old_payment.get("bank_accounts", [])
    new_bank = new_payment.get("bank_accounts", [])
    if old_bank != new_bank:
        old_acc_nums = {acc.get("account_number") for acc in old_bank}
        new_acc_nums = {acc.get("account_number") for acc in new_bank}

        added = [
            acc for acc in new_bank if acc.get("account_number") not in old_acc_nums
        ]
        removed = [
            acc for acc in old_bank if acc.get("account_number") not in new_acc_nums
        ]

        changes["bank_accounts"] = {"added": added, "removed": removed, "modified": []}

    # Cash payment
    old_cash = old_payment.get("cash_payment", {})
    new_cash = new_payment.get("cash_payment", {})
    if old_cash != new_cash:
        cash_changes = {}
        for field in ["address", "building", "office", "open_days", "open_hours"]:
            if old_cash.get(field) != new_cash.get(field):
                cash_changes[field] = {
                    "from": old_cash.get(field),
                    "to": new_cash.get(field),
                }
        if cash_changes:
            changes["cash_payment"] = cash_changes

    # Success message
    if old_data.get("success_message") != new_data.get("success_message"):
        changes["success_message"] = {
            "from": old_data.get("success_message"),
            "to": new_data.get("success_message"),
        }

    return changes


# ============================================
# ADMIN ENDPOINT (Protected)
# ============================================


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def admin_form_settings(request):
    """
    GET: Retrieve form settings with metadata
    PUT: Update form settings

    Requires authentication. All admins can access.
    """
    settings = FormSettings.get_settings()

    if request.method == "GET":
        serializer = AdminFormSettingsResponseSerializer(settings)
        return Response(
            {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
        )

    elif request.method == "PUT":
        serializer = AdminFormSettingsSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Validation failed",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        validated_data = serializer.validated_data

        # Capture old data for change tracking
        old_data = AdminFormSettingsSerializer().to_representation(settings)

        # Prepare new data (use snake_case keys from validated_data)
        payment_settings = validated_data.get("payment_settings", {})
        new_data = {
            "membership_fee": float(validated_data["membership_fee"]),
            "payment_settings": {
                "gcash_accounts": payment_settings.get("gcash_accounts", []),
                "bank_accounts": payment_settings.get("bank_accounts", []),
                "cash_payment": payment_settings.get("cash_payment", {}),
            },
            "success_message": validated_data.get("success_message", ""),
        }

        # Update the settings
        settings.membership_fee = validated_data["membership_fee"]
        settings.gcash_accounts = payment_settings.get("gcash_accounts", [])
        settings.bank_accounts = payment_settings.get("bank_accounts", [])
        settings.cash_payment = payment_settings.get("cash_payment", {})
        settings.success_message = validated_data.get("success_message", "")
        settings.updated_by = request.user
        settings.save()

        # Generate change notes and log to activity log
        change_notes = generate_change_notes(old_data, new_data)
        changes_json = build_changes_json(old_data, new_data)

        # Only log if there were actual changes
        if changes_json:
            ip_address = request.META.get("REMOTE_ADDR")

            # Log to AdminActivityLog
            AdminActivityLog.objects.create(
                admin=request.user,
                action="form_settings_updated",
                target_type="form_settings",
                target_id=None,
                notes=change_notes,
                ip_address=ip_address,
            )

            # Log detailed changes to FormSettingsHistory
            FormSettingsHistory.objects.create(admin=request.user, changes=changes_json)

        # Return updated settings
        response_serializer = AdminFormSettingsResponseSerializer(settings)
        return Response(
            {
                "success": True,
                "message": "Form settings updated successfully",
                "data": response_serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ============================================
# PUBLIC ENDPOINT (No Auth Required)
# ============================================


@api_view(["GET"])
@permission_classes([AllowAny])
def public_form_settings(request):
    """
    GET: Retrieve form settings for registration form.

    Returns only the information needed for the registration form.
    Does NOT include modification history or admin details.
    No authentication required.
    """
    settings = FormSettings.get_settings()
    serializer = PublicFormSettingsSerializer(settings)

    return Response(
        {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
    )
