# Alumni Registration System - Backend API

## 📁 Project Structure
```
alumni-reg_api/
├── config/
│   ├── __init__.py
│   ├── settings.py          # Main Django settings
│   ├── urls.py              # Root URL configuration
│   ├── utils.py             # Custom utilities (exception handler)
│   └── wsgi.py
│
├── applications/
│   ├── management/
│   │   └── commands/
│   │       └── seed_data.py  # Seed reference data
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py             # Admin panel configuration
│   ├── models.py            # Main models (Application, Province, etc.)
│   ├── serializers.py       # API serializers
│   ├── views.py             # API views
│   ├── urls.py              # Public registration endpoints
│   ├── verification_urls.py # Admin verification endpoints
│   ├── rejected_urls.py     # Rejected applicants endpoints
│   └── dashboard_urls.py    # Dashboard endpoints
│
├── members/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── models.py            # Member model
│   ├── serializers.py       # Member serializers
│   ├── views.py             # Member views
│   └── urls.py              # Member endpoints
│
├── accounts/
│   ├── __init__.py
│   ├── serializers.py       # Auth serializers
│   ├── views.py             # Auth views (login, logout, verify)
│   └── urls.py              # Auth endpoints
│
├── venv/                    # Virtual environment (not in git)
├── .env                     # Environment variables (not in git)
├── .gitignore
├── manage.py
├── requirements.txt         # Python dependencies
├── test_api.py             # API test script
└── README.md               # This file
```

---

## 📦 Prerequisites

- **Python 3.12+**
- **MySQL 8.0+**
- **pip** (Python package manager)
- **MySQL Workbench** (optional, for database management)

---

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/kapadilla/alumni-reg_api.git
cd alumni-reg_api
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### 1. Create Environment File

Create a `.env` file in the project root:
```bash
# Generate a secret key (run in Python):
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Then create `.env`:
```env
# Django Settings
SECRET_KEY=your-generated-secret-key-here
DEBUG=True

# MySQL Database
DB_NAME=db_alumni_reg
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440
```

### 2. Update CORS Settings

In `config/settings.py`, update allowed origins if needed:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",      # Nuxt/Vue frontend
    "http://127.0.0.1:3000",
    # Add your frontend URL here
]
```

---

## 🗄️ Database Setup

### 1. Create MySQL Database

### 2. Run Migrations
```bash
# Create migration files
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### 3. Seed Reference Data
```bash
python manage.py seed_data
```

### 4. Create Superuser (Admin Account)
```bash
python manage.py createsuperuser
```

Follow the prompts:
- Email: `admin@example.com`
- Password: (choose a secure password)

---

## 🏃 Running the Application

### Start the Development Server
```bash
python manage.py runserver
```

The API will be available at: **http://localhost:8000**

### Access the Admin Panel

Navigate to: **http://localhost:8000/admin**

Login with your superuser credentials.

---

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api
```

### Authentication

Most endpoints require a JWT token. Include it in the header:
```
Authorization: Bearer YOUR_TOKEN_HERE
```

### Endpoint Categories

#### 1. **Authentication** (`/api/auth/`)
- `POST /login/` - Admin login
- `POST /logout/` - Admin logout
- `GET /verify/` - Verify token validity

#### 2. **Registration** (`/api/registration/`)
- `POST /submit/` - Submit new registration (public)
- `GET /check-email/` - Check email availability (public)

#### 3. **Reference Data** (`/api/registration/reference/`)
- `GET /provinces/` - List all provinces
- `GET /cities/?province=<name>` - List cities by province
- `GET /barangays/?city=<name>` - List barangays by city
- `GET /degree-programs/` - List all degree programs

#### 4. **Alumni Verification** (`/api/verification/alumni/`) 🔒
- `GET /` - List pending alumni verifications
- `GET /<id>/` - Get application details
- `POST /<id>/verify/` - Verify as alumni
- `POST /<id>/reject/` - Reject application
- `GET /export/` - Export to CSV

#### 5. **Payment Verification** (`/api/verification/payment/`) 🔒
- `GET /` - List pending payment verifications
- `GET /<id>/` - Get application details
- `POST /<id>/confirm/` - Confirm payment
- `POST /<id>/reject/` - Reject application
- `GET /export/` - Export to CSV

#### 6. **Rejected Applicants** (`/api/rejected/`) 🔒
- `GET /` - List all rejected applicants
- `GET /<id>/` - Get rejected applicant details
- `GET /export/` - Export to CSV

#### 7. **Members** (`/api/members/`) 🔒
- `GET /` - List all approved members
- `GET /<id>/` - Get member details
- `PUT /<id>/update/` - Update member information
- `DELETE /<id>/revoke/` - Revoke membership
- `GET /export/` - Export to CSV

#### 8. **Dashboard** (`/api/dashboard/`) 🔒
- `GET /stats/` - Get statistics
- `GET /activity/` - Get recent activity

🔒 = Requires authentication

### Request/Response Format

**Success Response:**
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... }
}
```

**Error Response:**
```json
{
  "success": false,
  "message": "Error message",
  "errors": { ... }
}
```

### Example: Submit Registration

**Request:**
```bash
curl -X POST http://localhost:8000/api/registration/submit/ \
  -H "Content-Type: application/json" \
  -d '{
    "personalDetails": {
      "title": "Mr",
      "firstName": "Juan",
      "lastName": "Dela Cruz",
      "dateOfBirth": "1995-05-15",
      "email": "juan@example.com",
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
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Registration submitted successfully",
  "data": {
    "applicationId": 1,
    "status": "pending_alumni_verification",
    "submittedAt": "2025-01-03T10:30:00Z"
  }
}
```

---

## 🧪 Testing

### Using the Test Script
```bash
python test_api.py
```

**Before running, update credentials in `test_api.py`:**
```python
login_data = {
    "email": "admin@example.com",      # Your admin email
    "password": "your_password_here"   # Your admin password
}
```

---

## 🎉 Acknowledgments

- Django REST Framework team
- UP Cebu Alumni Association
- All contributors

---

## 📅 Changelog

### Version 1.0.0 (2025-01-03)
- Initial release
- Complete two-step verification system
- JWT authentication
- CSV export functionality
- Comprehensive API documentation

---

**Made with ❤️ for UP Cebu Alumni Association**