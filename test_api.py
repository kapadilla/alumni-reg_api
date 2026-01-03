import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

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

# Store token
token = None

# 1. REFERENCE DATA
print_section("1. REFERENCE DATA ENDPOINTS")

test_endpoint("GET", f"{BASE_URL}/registration/reference/provinces/")
test_endpoint("GET", f"{BASE_URL}/registration/reference/cities/", params={"province": "Cebu"})
test_endpoint("GET", f"{BASE_URL}/registration/reference/barangays/", params={"city": "Cebu City"})
test_endpoint("GET", f"{BASE_URL}/registration/reference/degree-programs/")

# 2. REGISTRATION
print_section("2. REGISTRATION ENDPOINTS")

# Check email
test_endpoint("GET", f"{BASE_URL}/registration/check-email/", params={"email": "test@example.com"})

# Submit registration (both formats work!)
unique_email = f"juan.test{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"

# Test with camelCase (frontend style)
registration_data = {
    "personalDetails": {
        "title": "Mr",
        "firstName": "Juan",
        "lastName": "Dela Cruz",
        "dateOfBirth": "1995-05-15",
        "email": unique_email,
        "mobileNumber": "09171234567",
        "currentAddress": "123 Main St",
        "province": "Cebu",
        "city": "Cebu City",
        "barangay": "Lahug"
    },
    "academicStatus": {
        "degreeProgram": "Bachelor of Science in Computer Science",
        "yearGraduated": "2020",
        "studentNumber": "2016-12345"
    },
    "professional": {
        "currentEmployer": "Acme Corp",
        "jobTitle": "Software Developer",
        "industry": "Technology"
    },
    "membership": {
        "paymentMethod": "gcash"
    }
}

response = test_endpoint("POST", f"{BASE_URL}/registration/submit/", data=registration_data)
if response and response.status_code == 201:
    app_id = response.json()['data']['applicationId']
    print(f"\n✅ Application ID: {app_id}")

# 3. AUTHENTICATION
print_section("3. AUTHENTICATION")

login_data = {
    "email": "admin@example.com",  # Change to your admin email
    "password": "your_password"     # Change to your admin password
}

response = test_endpoint("POST", f"{BASE_URL}/auth/login/", data=login_data)
if response and response.status_code == 200:
    token = response.json()['data']['token']
    print(f"\n✅ Token obtained: {token[:50]}...")

if not token:
    print("\n❌ Could not get auth token. Create superuser first:")
    print("   python manage.py createsuperuser")
    exit()

headers = {"Authorization": f"Bearer {token}"}

# Verify token
test_endpoint("GET", f"{BASE_URL}/auth/verify/", headers=headers)

# 4. ALUMNI VERIFICATION
print_section("4. ALUMNI VERIFICATION ENDPOINTS")

test_endpoint("GET", f"{BASE_URL}/verification/alumni/", headers=headers)
if app_id:
    test_endpoint("GET", f"{BASE_URL}/verification/alumni/{app_id}/", headers=headers)
    test_endpoint("POST", f"{BASE_URL}/verification/alumni/{app_id}/verify/", 
                 headers=headers, data={"notes": "Verified from records"})

# 5. PAYMENT VERIFICATION
print_section("5. PAYMENT VERIFICATION ENDPOINTS")

test_endpoint("GET", f"{BASE_URL}/verification/payment/", headers=headers)
if app_id:
    test_endpoint("GET", f"{BASE_URL}/verification/payment/{app_id}/", headers=headers)
    test_endpoint("POST", f"{BASE_URL}/verification/payment/{app_id}/confirm/", 
                 headers=headers, data={"notes": "Payment received"})

# 6. MEMBERS
print_section("6. MEMBERS ENDPOINTS")

test_endpoint("GET", f"{BASE_URL}/members/", headers=headers)

# 7. DASHBOARD
print_section("7. DASHBOARD ENDPOINTS")

test_endpoint("GET", f"{BASE_URL}/dashboard/stats/", headers=headers)
test_endpoint("GET", f"{BASE_URL}/dashboard/activity/", headers=headers, params={"limit": 5})

# 8. REJECTED
print_section("8. REJECTED APPLICANTS ENDPOINTS")

test_endpoint("GET", f"{BASE_URL}/rejected/", headers=headers)

# 9. LOGOUT
print_section("9. LOGOUT")

test_endpoint("POST", f"{BASE_URL}/auth/logout/", headers=headers)

print("\n" + "=" * 70)
print(" ALL TESTS COMPLETE!")
print("=" * 70)