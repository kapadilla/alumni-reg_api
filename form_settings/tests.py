"""
Test cases for the form_settings app.
Tests for FormSettings model, API endpoints, and management commands.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from .models import FormSettings, FormSettingsHistory


class FormSettingsModelTestCase(TestCase):
    """Test cases for the FormSettings model"""

    def test_singleton_pattern(self):
        """Test that only one FormSettings instance can exist"""
        settings1 = FormSettings.objects.create(
            membership_fee=1450.00,
            gcash_accounts=[],
            bank_accounts=[],
        )
        # Creating another instance should use id=1
        settings2 = FormSettings(
            id=2,  # Try to use different id
            membership_fee=1500.00,
        )
        settings2.save()

        # Both should have id=1
        self.assertEqual(settings1.id, 1)
        self.assertEqual(settings2.id, 1)
        
        # Only one record should exist
        self.assertEqual(FormSettings.objects.count(), 1)

    def test_get_settings_creates_if_not_exists(self):
        """Test get_settings class method creates singleton if not exists"""
        self.assertEqual(FormSettings.objects.count(), 0)
        
        settings = FormSettings.get_settings()
        
        self.assertEqual(FormSettings.objects.count(), 1)
        self.assertEqual(settings.id, 1)
        self.assertEqual(settings.membership_fee, Decimal("1450.00"))

    def test_get_settings_returns_existing(self):
        """Test get_settings returns existing settings"""
        FormSettings.objects.create(
            membership_fee=2000.00,
            gcash_accounts=[{"name": "Test", "number": "09171234567"}],
        )
        
        settings = FormSettings.get_settings()
        
        self.assertEqual(settings.membership_fee, Decimal("2000.00"))
        self.assertEqual(len(settings.gcash_accounts), 1)

    def test_default_values(self):
        """Test default values are set correctly"""
        settings = FormSettings.get_settings()
        
        self.assertEqual(settings.membership_fee, Decimal("1450.00"))
        self.assertEqual(settings.gcash_accounts, [])
        self.assertEqual(settings.bank_accounts, [])
        self.assertEqual(settings.success_message, "")

    def test_string_representation(self):
        """Test string representation includes update timestamp"""
        settings = FormSettings.get_settings()
        self.assertIn("Form Settings", str(settings))


class FormSettingsHistoryModelTestCase(TestCase):
    """Test cases for the FormSettingsHistory model"""

    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_user(
            username="historytest@example.com",
            email="historytest@example.com",
            password="testpass123",
            is_staff=True,
        )

    def test_history_creation(self):
        """Test history record can be created"""
        history = FormSettingsHistory.objects.create(
            admin=self.admin_user,
            changes={"membership_fee": {"old": "1450.00", "new": "1500.00"}},
        )
        
        self.assertIsNotNone(history.id)
        self.assertIsNotNone(history.changed_at)

    def test_history_ordering(self):
        """Test history is ordered by most recent first"""
        FormSettingsHistory.objects.create(
            admin=self.admin_user,
            changes={"field": "first"},
        )
        FormSettingsHistory.objects.create(
            admin=self.admin_user,
            changes={"field": "second"},
        )
        
        histories = FormSettingsHistory.objects.all()
        self.assertEqual(histories[0].changes["field"], "second")


class FormSettingsAPITestCase(APITestCase):
    """Test cases for the form settings API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.settings_url = "/api/v1/form-settings/"
        self.public_settings_url = "/api/v1/form-settings/public/"
        self.history_url = "/api/v1/form-settings/history/"

        # Create admin user
        self.admin_user = User.objects.create_user(
            username="formsettingsadmin@example.com",
            email="formsettingsadmin@example.com",
            password="testpass123",
            first_name="Form",
            last_name="Admin",
            is_staff=True,
        )

        # Create form settings
        self.settings = FormSettings.get_settings()

        # Login to get token
        login_response = self.client.post(
            "/api/v1/auth/login/",
            {"email": "formsettingsadmin@example.com", "password": "testpass123"},
            format="json",
        )
        self.token = login_response.data["data"]["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_get_settings_authenticated(self):
        """Test getting form settings when authenticated"""
        response = self.client.get(self.settings_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("membershipFee", response.data["data"])

    def test_get_settings_unauthenticated(self):
        """Test that unauthenticated users cannot get full settings"""
        self.client.credentials()  # Remove auth
        response = self.client.get(self.settings_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_public_settings(self):
        """Test getting public form settings (unauthenticated)"""
        self.client.credentials()  # Remove auth
        response = self.client.get(self.public_settings_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        # Public endpoint should include payment info
        self.assertIn("membershipFee", response.data["data"])

    def test_update_settings(self):
        """Test updating form settings"""
        update_data = {
            "membershipFee": "1500.00",
            "successMessage": "Thank you for registering!",
        }
        
        response = self.client.put(self.settings_url, update_data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        
        # Verify update persisted
        self.settings.refresh_from_db()
        self.assertEqual(self.settings.membership_fee, Decimal("1500.00"))
        self.assertEqual(self.settings.success_message, "Thank you for registering!")

    def test_update_creates_history(self):
        """Test that updating settings creates a history record"""
        initial_history_count = FormSettingsHistory.objects.count()
        
        update_data = {"membershipFee": "1600.00"}
        self.client.put(self.settings_url, update_data, format="json")
        
        # Should have one more history record
        self.assertEqual(FormSettingsHistory.objects.count(), initial_history_count + 1)

    def test_update_gcash_accounts(self):
        """Test updating GCash accounts"""
        update_data = {
            "gcashAccounts": [
                {"name": "John Doe", "number": "09171234567"},
                {"name": "Jane Doe", "number": "09181234567"},
            ]
        }
        
        response = self.client.put(self.settings_url, update_data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.settings.refresh_from_db()
        self.assertEqual(len(self.settings.gcash_accounts), 2)

    def test_update_bank_accounts(self):
        """Test updating bank accounts"""
        update_data = {
            "bankAccounts": [
                {
                    "bankName": "BDO",
                    "accountName": "Alumni Association",
                    "accountNumber": "1234567890",
                },
            ]
        }
        
        response = self.client.put(self.settings_url, update_data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.settings.refresh_from_db()
        self.assertEqual(len(self.settings.bank_accounts), 1)
        self.assertEqual(self.settings.bank_accounts[0]["bankName"], "BDO")

    def test_update_cash_payment(self):
        """Test updating cash payment details"""
        update_data = {
            "cashPayment": {
                "address": "123 Main Street",
                "building": "Admin Building",
                "office": "Room 101",
                "openDays": ["Monday", "Tuesday", "Wednesday"],
                "openHours": "8:00 AM - 5:00 PM",
            }
        }
        
        response = self.client.put(self.settings_url, update_data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.settings.refresh_from_db()
        self.assertEqual(self.settings.cash_payment["address"], "123 Main Street")
        self.assertEqual(len(self.settings.cash_payment["openDays"]), 3)

    def test_get_history(self):
        """Test getting form settings history"""
        # Create some history
        FormSettingsHistory.objects.create(
            admin=self.admin_user,
            changes={"membership_fee": {"old": "1450.00", "new": "1500.00"}},
        )
        
        response = self.client.get(self.history_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])


class SeedFormSettingsCommandTestCase(TestCase):
    """Test cases for the seed_form_settings management command"""

    def test_seed_creates_settings(self):
        """Test that seed command creates form settings"""
        from django.core.management import call_command
        from io import StringIO
        
        self.assertEqual(FormSettings.objects.count(), 0)
        
        out = StringIO()
        call_command("seed_form_settings", stdout=out)
        
        self.assertEqual(FormSettings.objects.count(), 1)
        self.assertIn("created successfully", out.getvalue())

    def test_seed_skips_if_exists(self):
        """Test that seed command skips if settings already exist"""
        from django.core.management import call_command
        from io import StringIO
        
        # Create settings first
        FormSettings.get_settings()
        
        out = StringIO()
        call_command("seed_form_settings", stdout=out)
        
        self.assertEqual(FormSettings.objects.count(), 1)
        self.assertIn("already exist", out.getvalue())
