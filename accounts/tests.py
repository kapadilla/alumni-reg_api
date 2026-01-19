from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status


class AuthenticationAPITestCase(APITestCase):
    """Test cases for the authentication API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.login_url = "/api/v1/auth/login/"
        self.logout_url = "/api/v1/auth/logout/"
        self.verify_url = "/api/v1/auth/verify/"
        self.admins_url = "/api/v1/auth/admins/"

        # Create a test admin user
        self.admin_user = User.objects.create_user(
            username="testadmin@example.com",
            email="testadmin@example.com",
            password="testpass123",
            first_name="Test",
            last_name="Admin",
            is_staff=True,
        )

    def test_login_success(self):
        """Test successful admin login"""
        response = self.client.post(
            self.login_url,
            {"email": "testadmin@example.com", "password": "testpass123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("token", response.data["data"])
        self.assertIn("refresh", response.data["data"])

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post(
            self.login_url,
            {"email": "testadmin@example.com", "password": "wrongpassword"},
            format="json",
        )

        # API returns 400 Bad Request for invalid credentials
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_token(self):
        """Test token verification"""
        # First login to get token
        login_response = self.client.post(
            self.login_url,
            {"email": "testadmin@example.com", "password": "testpass123"},
            format="json",
        )

        token = login_response.data["data"]["token"]

        # Verify the token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get(self.verify_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["data"]["valid"])

    def test_protected_endpoint_without_auth(self):
        """Test that protected endpoints require authentication"""
        response = self.client.get(self.admins_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_admins_authenticated(self):
        """Test listing admins when authenticated"""
        # Login first
        login_response = self.client.post(
            self.login_url,
            {"email": "testadmin@example.com", "password": "testpass123"},
            format="json",
        )

        token = login_response.data["data"]["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get(self.admins_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
