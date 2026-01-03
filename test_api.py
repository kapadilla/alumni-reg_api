import requests
import json

BASE_URL = "http://localhost:8000/api/registration"

registration_data = {
    "personal_details": { 
        "title": "Mr",
        "firstName": "Juan",
        "lastName": "Dela Cruz",
        "dateOfBirth": "1995-05-15",
        "email": "juan.delacruz@example.com",
        "mobileNumber": "09171234567",
        "currentAddress": "123 Main St",
        "province": "Cebu",
        "city": "Cebu City",
        "barangay": "Lahug"
    },
    "academic_status": { 
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

response = requests.post(f"{BASE_URL}/submit/", json=registration_data)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")