from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import MembershipApplication, VerificationHistory


class RegistrationAPITestCase(APITestCase):
    """Test cases for the registration API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.submit_url = "/api/v1/registration/submit/"
        self.check_email_url = "/api/v1/registration/check-email/"

        # Valid registration data matching registration_form_fields.md
        self.valid_registration_data = {
            "personalDetails": {
                "firstName": "Juan",
                "middleName": "Santos",
                "lastName": "Dela Cruz",
                "suffix": "Jr.",
                "maidenName": "",
                "dateOfBirth": "1995-05-15",
                "email": "juan.test@example.com",
                "mobileNumber": "09171234567",
                "currentAddress": "123 Main St",
                "province": "Cebu",
                "city": "Cebu City",
                "barangay": "Lahug",
                "zipCode": "6000",
            },
            "academicStatus": {
                "campus": "UP Cebu",
                "degreeProgram": "Bachelor of Science in Computer Science",
                "yearGraduated": "2020",
                "studentNumber": "2016-12345",
            },
            "professional": {
                "currentEmployer": "Acme Corp",
                "jobTitle": "Software Developer",
                "industry": "Technology",
                "yearsOfExperience": "5",
            },
            "membership": {
                "paymentMethod": "cash",
                "cashPaymentDate": "2026-01-19",
                "cashReceivedBy": "Admin Staff",
            },
            "mentorship": {"joinMentorshipProgram": False},
        }

    def test_check_email_available(self):
        """Test email availability check - available email"""
        response = self.client.get(self.check_email_url, {"email": "new@example.com"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["data"]["available"])

    def test_check_email_up_domain_blocked(self):
        """Test that @up.edu.ph emails are blocked"""
        response = self.client.get(self.check_email_url, {"email": "test@up.edu.ph"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["data"]["available"])

    def test_submit_registration_cash_payment(self):
        """Test successful registration with cash payment"""
        response = self.client.post(
            self.submit_url, self.valid_registration_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertIn("applicationId", response.data["data"])

        # Verify application was created
        app = MembershipApplication.objects.get(
            id=response.data["data"]["applicationId"]
        )
        self.assertEqual(app.first_name, "Juan")
        self.assertEqual(app.campus, "UP Cebu")
        self.assertEqual(app.status, "pending_alumni_verification")

    def test_submit_registration_campus_required(self):
        """Test that campus field is required"""
        data = self.valid_registration_data.copy()
        data["academicStatus"] = {
            "degreeProgram": "Bachelor of Science in Computer Science",
            "yearGraduated": "2020",
            # campus is missing
        }
        data["personalDetails"] = self.valid_registration_data["personalDetails"].copy()
        data["personalDetails"]["email"] = "test2@example.com"

        response = self.client.post(self.submit_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_submit_registration_degree_program_required(self):
        """Test that degreeProgram field is required"""
        data = self.valid_registration_data.copy()
        data["academicStatus"] = {
            "campus": "UP Cebu",
            "yearGraduated": "2020",
            # degreeProgram is missing
        }
        data["personalDetails"] = self.valid_registration_data["personalDetails"].copy()
        data["personalDetails"]["email"] = "test3@example.com"

        response = self.client.post(self.submit_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_submit_registration_duplicate_email(self):
        """Test that duplicate emails are rejected"""
        # First registration
        response1 = self.client.post(
            self.submit_url, self.valid_registration_data, format="json"
        )
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        # Second registration with same email
        response2 = self.client.post(
            self.submit_url, self.valid_registration_data, format="json"
        )
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_submit_registration_gcash_requires_reference(self):
        """Test that GCash payment requires reference number"""
        data = self.valid_registration_data.copy()
        data["personalDetails"] = self.valid_registration_data["personalDetails"].copy()
        data["personalDetails"]["email"] = "gcash@example.com"
        data["membership"] = {
            "paymentMethod": "gcash"
            # gcashReferenceNumber is missing
        }

        response = self.client.post(self.submit_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_submit_registration_bank_requires_fields(self):
        """Test that bank payment requires all bank fields"""
        data = self.valid_registration_data.copy()
        data["personalDetails"] = self.valid_registration_data["personalDetails"].copy()
        data["personalDetails"]["email"] = "bank@example.com"
        data["membership"] = {
            "paymentMethod": "bank"
            # bank fields are missing
        }

        response = self.client.post(self.submit_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_submit_registration_mentorship_requires_fields_when_opted_in(self):
        """Test mentorship fields are required when joinMentorshipProgram is true"""
        data = self.valid_registration_data.copy()
        data["personalDetails"] = self.valid_registration_data["personalDetails"].copy()
        data["personalDetails"]["email"] = "mentor@example.com"
        data["mentorship"] = {
            "joinMentorshipProgram": True
            # Required mentorship fields are missing
        }

        response = self.client.post(self.submit_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_submit_registration_valid_mentorship(self):
        """Test successful registration with mentorship program"""
        data = self.valid_registration_data.copy()
        data["personalDetails"] = self.valid_registration_data["personalDetails"].copy()
        data["personalDetails"]["email"] = "mentor2@example.com"
        data["mentorship"] = {
            "joinMentorshipProgram": True,
            "mentorshipAreas": ["career-advancement", "technology-innovation"],
            "mentorshipIndustryTracks": ["it-software"],
            "mentorshipFormat": "one-on-one",
            "mentorshipAvailability": "4",
        }

        response = self.client.post(self.submit_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify mentorship data was saved
        app = MembershipApplication.objects.get(
            id=response.data["data"]["applicationId"]
        )
        self.assertTrue(app.join_mentorship_program)
        self.assertEqual(app.mentorship_format, "one-on-one")


class MembershipApplicationModelTestCase(TestCase):
    """Test cases for the MembershipApplication model"""

    def test_campus_default_value(self):
        """Test that campus has default value 'UP Cebu'"""
        app = MembershipApplication(
            first_name="Test",
            last_name="User",
            date_of_birth="1995-01-01",
            email="model_test@example.com",
            mobile_number="09171234567",
            current_address="123 Test St",
            province="Cebu",
            city="Cebu City",
            barangay="Lahug",
            degree_program="BS Computer Science",
            payment_method="cash",
        )
        app.save()

        self.assertEqual(app.campus, "UP Cebu")

    def test_full_name_property(self):
        """Test the full_name property"""
        app = MembershipApplication(
            first_name="Juan",
            last_name="Dela Cruz",
            suffix="Jr.",
            date_of_birth="1995-01-01",
            email="fullname@example.com",
            mobile_number="09171234567",
            current_address="123 Test St",
            province="Cebu",
            city="Cebu City",
            barangay="Lahug",
            degree_program="BS Computer Science",
            payment_method="cash",
        )

        self.assertEqual(app.full_name, "Juan Dela Cruz Jr.")

    def test_status_choices(self):
        """Test that status field has correct choices"""
        valid_statuses = [
            "pending_alumni_verification",
            "pending_payment_verification",
            "approved",
            "rejected",
            "revoked",
        ]

        for status_value in valid_statuses:
            app = MembershipApplication(
                first_name="Test",
                last_name="User",
                date_of_birth="1995-01-01",
                email=f"status_{status_value}@example.com",
                mobile_number="09171234567",
                current_address="123 Test St",
                province="Cebu",
                city="Cebu City",
                barangay="Lahug",
                degree_program="BS Computer Science",
                payment_method="cash",
                status=status_value,
            )
            app.save()
            self.assertEqual(app.status, status_value)
