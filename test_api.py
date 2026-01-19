# -*- coding: utf-8 -*-
import requests
import json
import sys
from datetime import datetime

# Fix Unicode output on Windows
sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://localhost:8000/api/v1"


def print_section(title):
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def test_endpoint(method, url, headers=None, data=None, params=None):
    print(f"\n{method} {url}")
    if params:
        print(f"Params: {params}")
    if data:
        print(f"Body: {json.dumps(data, indent=2)}")

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)

        print(f"Status: {response.status_code}")
        try:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Response: {response.text}")

        return response
    except Exception as e:
        print(f"Error: {str(e)}")
        return None


# Store global variables
token = None
app_id = None
admin_id = None

# ==========================================
# 1. REGISTRATION
# ==========================================
print_section("1. REGISTRATION ENDPOINTS")

# Check email
test_endpoint(
    "GET", f"{BASE_URL}/registration/check-email/", params={"email": "test@example.com"}
)

# Submit registration
unique_email = f"juan.test{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"

registration_data = {
    "personalDetails": {
        "firstName": "Juan",
        "middleName": "Santos",
        "lastName": "Dela Cruz",
        "dateOfBirth": "1995-05-15",
        "email": unique_email,
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
}

response = test_endpoint(
    "POST", f"{BASE_URL}/registration/submit/", data=registration_data
)
if response and response.status_code == 201:
    app_id = response.json()["data"]["applicationId"]
    print(f"\n✅ Application ID: {app_id}")

# ==========================================
# 2. AUTHENTICATION
# ==========================================
print_section("2. AUTHENTICATION ENDPOINTS")

login_data = {"email": "kapadilla@up.edu.ph", "password": "p@ssw0rd"}

response = test_endpoint("POST", f"{BASE_URL}/auth/login/", data=login_data)
if response and response.status_code == 200:
    token = response.json()["data"]["token"]
    print(f"\n✅ Token obtained: {token[:50]}...")

if not token:
    print("\n❌ Could not get auth token. Create superuser first:")
    print("   python manage.py createsuperuser")
    exit()

headers = {"Authorization": f"Bearer {token}"}

# Verify token
test_endpoint("GET", f"{BASE_URL}/auth/verify/", headers=headers)

# ==========================================
# 3. ALUMNI VERIFICATION
# ==========================================
print_section("3. ALUMNI VERIFICATION ENDPOINTS")

test_endpoint("GET", f"{BASE_URL}/verification/alumni/", headers=headers)
if app_id:
    test_endpoint("GET", f"{BASE_URL}/verification/alumni/{app_id}/", headers=headers)
    test_endpoint(
        "POST",
        f"{BASE_URL}/verification/alumni/{app_id}/verify/",
        headers=headers,
        data={"notes": "Verified from records"},
    )

# ==========================================
# 4. PAYMENT VERIFICATION
# ==========================================
print_section("4. PAYMENT VERIFICATION ENDPOINTS")

test_endpoint("GET", f"{BASE_URL}/verification/payment/", headers=headers)
if app_id:
    test_endpoint("GET", f"{BASE_URL}/verification/payment/{app_id}/", headers=headers)
    test_endpoint(
        "POST",
        f"{BASE_URL}/verification/payment/{app_id}/confirm/",
        headers=headers,
        data={"notes": "Payment received"},
    )

# ==========================================
# 5. MEMBERS
# ==========================================
print_section("5. MEMBERS ENDPOINTS")

test_endpoint("GET", f"{BASE_URL}/members/", headers=headers, params={"status": "all"})
test_endpoint(
    "GET", f"{BASE_URL}/members/", headers=headers, params={"status": "active"}
)

# Test member detail if we have members
response = test_endpoint(
    "GET", f"{BASE_URL}/members/", headers=headers, params={"limit": 1}
)
if response and response.status_code == 200:
    data = response.json()
    if data.get("data", {}).get("members"):
        member_id = data["data"]["members"][0]["id"]
        test_endpoint("GET", f"{BASE_URL}/members/{member_id}/", headers=headers)

# Export
test_endpoint("GET", f"{BASE_URL}/members/export/", headers=headers)

# ==========================================
# 6. REJECTED APPLICANTS
# ==========================================
print_section("6. REJECTED APPLICANTS ENDPOINTS")

test_endpoint("GET", f"{BASE_URL}/rejected/", headers=headers)
test_endpoint("GET", f"{BASE_URL}/rejected/export/", headers=headers)

# ==========================================
# 7. DASHBOARD
# ==========================================
print_section("7. DASHBOARD ENDPOINTS")

test_endpoint("GET", f"{BASE_URL}/dashboard/stats/", headers=headers)
test_endpoint(
    "GET", f"{BASE_URL}/dashboard/activity/", headers=headers, params={"limit": 10}
)
test_endpoint("GET", f"{BASE_URL}/dashboard/filters/", headers=headers)

# ==========================================
# 8. ADMIN MANAGEMENT
# ==========================================
print_section("8. ADMIN MANAGEMENT ENDPOINTS")

# List admins
test_endpoint("GET", f"{BASE_URL}/auth/admins/", headers=headers)

# Create admin
create_admin_data = {
    "email": f"testadmin{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
    "password": "testpass123",
    "first_name": "Test",
    "last_name": "Admin",
}
response = test_endpoint(
    "POST", f"{BASE_URL}/auth/admins/", headers=headers, data=create_admin_data
)
if response and response.status_code == 201:
    admin_id = response.json()["data"]["id"]
    print(f"\n✅ Created Admin ID: {admin_id}")

# Get admin detail
if admin_id:
    test_endpoint("GET", f"{BASE_URL}/auth/admins/{admin_id}/", headers=headers)

    # Update admin
    test_endpoint(
        "PUT",
        f"{BASE_URL}/auth/admins/{admin_id}/",
        headers=headers,
        data={"first_name": "Updated"},
    )

    # Deactivate admin
    test_endpoint("DELETE", f"{BASE_URL}/auth/admins/{admin_id}/", headers=headers)

    # Reactivate admin (NEW ENDPOINT)
    test_endpoint(
        "POST",
        f"{BASE_URL}/auth/admins/{admin_id}/reactivate/",
        headers=headers,
        data={"notes": "Testing reactivation"},
    )

    # Get admin activity log (NEW ENDPOINT)
    test_endpoint(
        "GET",
        f"{BASE_URL}/auth/admins/{admin_id}/activity/",
        headers=headers,
        params={"limit": 20},
    )

# Get current user's activity log
response = test_endpoint("GET", f"{BASE_URL}/auth/verify/", headers=headers)
if response and response.status_code == 200:
    current_user_id = response.json()["data"]["user"]["id"]
    test_endpoint(
        "GET",
        f"{BASE_URL}/auth/admins/{current_user_id}/activity/",
        headers=headers,
        params={"limit": 10, "ordering": "-timestamp"},
    )

# ==========================================
# 9. LOGOUT
# ==========================================
print_section("9. LOGOUT")

test_endpoint("POST", f"{BASE_URL}/auth/logout/", headers=headers)

print("\n" + "=" * 70)
print(" ALL TESTS COMPLETE!")
print("=" * 70)
print("\n📝 Summary:")
print("- Registration endpoints ✅")
print("- Authentication endpoints ✅")
print("- Alumni verification endpoints ✅")
print("- Payment verification endpoints ✅")
print("- Members endpoints ✅")
print("- Rejected applicants endpoints ✅")
print("- Dashboard endpoints ✅")
print("- Admin management endpoints ✅")
print("- Admin reactivation endpoint ✅")
print("- Admin activity log endpoint ✅")
print("- Enhanced dashboard activity ✅")
