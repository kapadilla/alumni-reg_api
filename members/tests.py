from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from applications.models import MembershipApplication, VerificationHistory
from .models import Member


class MembersAPITestCase(APITestCase):
    """Test cases for the members API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.members_url = "/api/v1/members/"

        # Create a test admin user
        self.admin_user = User.objects.create_user(
            username="memberadmin@example.com",
            email="memberadmin@example.com",
            password="testpass123",
            first_name="Member",
            last_name="Admin",
            is_staff=True,
        )

        # Create a test application (approved)
        self.application = MembershipApplication.objects.create(
            first_name="Test",
            last_name="Member",
            date_of_birth="1995-01-01",
            email="testmember@example.com",
            mobile_number="09171234567",
            current_address="123 Test St",
            province="Cebu",
            city="Cebu City",
            barangay="Lahug",
            campus="UP Cebu",
            degree_program="BS Computer Science",
            year_graduated="2020",
            payment_method="cash",
            status="approved",
        )

        # Create the member
        self.member = Member.objects.create(
            application=self.application, is_active=True
        )

        # Login to get token
        self.client.post(
            "/api/v1/auth/login/",
            {"email": "memberadmin@example.com", "password": "testpass123"},
            format="json",
        )

        login_response = self.client.post(
            "/api/v1/auth/login/",
            {"email": "memberadmin@example.com", "password": "testpass123"},
            format="json",
        )
        self.token = login_response.data["data"]["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_list_members(self):
        """Test listing all members"""
        response = self.client.get(self.members_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

    def test_list_active_members(self):
        """Test listing active members only"""
        response = self.client.get(self.members_url, {"status": "active"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

    def test_get_member_detail(self):
        """Test getting member detail"""
        response = self.client.get(f"{self.members_url}{self.member.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["academicStatus"]["campus"], "UP Cebu")

    def test_revoke_member(self):
        """Test revoking a member"""
        response = self.client.post(
            f"{self.members_url}{self.member.id}/revoke/",
            {"reason": "Test revocation"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refresh from database
        self.member.refresh_from_db()
        self.assertFalse(self.member.is_active)

    def test_reinstate_member(self):
        """Test reinstating a revoked member"""
        # First revoke the member
        self.member.is_active = False
        self.member.save()
        self.application.status = "revoked"
        self.application.save()

        response = self.client.post(
            f"{self.members_url}{self.member.id}/reinstate/",
            {"notes": "Test reinstatement"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refresh from database
        self.member.refresh_from_db()
        self.assertTrue(self.member.is_active)


class MemberModelTestCase(TestCase):
    """Test cases for the Member model"""

    def setUp(self):
        """Set up test data"""
        self.application = MembershipApplication.objects.create(
            first_name="Model",
            last_name="Test",
            date_of_birth="1995-01-01",
            email="modeltest@example.com",
            mobile_number="09171234567",
            current_address="123 Test St",
            province="Cebu",
            city="Cebu City",
            barangay="Lahug",
            campus="UP Cebu",
            degree_program="BS Computer Science",
            payment_method="cash",
            status="approved",
        )

    def test_member_creation(self):
        """Test member can be created from application"""
        member = Member.objects.create(application=self.application, is_active=True)

        self.assertTrue(member.is_active)
        self.assertEqual(member.application.campus, "UP Cebu")

    def test_member_str(self):
        """Test member string representation"""
        member = Member.objects.create(application=self.application, is_active=True)

        self.assertIn("Model Test", str(member))
