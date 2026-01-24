# Alumni Registration System - Backend API

## 📁 Project Structure
```
alumni-reg_api/
├── config/                          # Django project configuration
│   ├── management/
│   │   └── commands/
│   │       └── setup_db.py          # Unified database setup command
│   ├── __init__.py
│   ├── settings.py                  # Main Django settings
│   ├── urls.py                      # Root URL configuration
│   ├── utils.py                     # Custom utilities (exception handler)
│   ├── asgi.py
│   └── wsgi.py
│
├── applications/                    # Core application handling
│   ├── management/
│   │   └── commands/
│   │       └── seed_mock_data.py    # Generate mock test data
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py                     # Admin panel configuration
│   ├── models.py                    # MembershipApplication, VerificationHistory
│   ├── serializers.py               # API serializers
│   ├── views.py                     # API views
│   ├── urls.py                      # Public registration endpoints
│   ├── verification_urls.py         # Admin verification endpoints
│   ├── rejected_urls.py             # Rejected applicants endpoints
│   ├── dashboard_urls.py            # Dashboard endpoints
│   └── tests.py                     # Unit tests
│
├── members/                         # Member management
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── models.py                    # Member model
│   ├── serializers.py               # Member serializers
│   ├── views.py                     # Member views
│   ├── urls.py                      # Member endpoints
│   └── tests.py                     # Unit tests
│
├── accounts/                        # Authentication & admin management
│   ├── migrations/
│   ├── __init__.py
│   ├── models.py                    # AdminActivityLog model
│   ├── serializers.py               # Auth serializers
│   ├── views.py                     # Auth views (login, logout, admins)
│   ├── urls.py                      # Auth endpoints
│   └── tests.py                     # Unit tests
│
├── form_settings/                   # Registration form configuration
│   ├── management/
│   │   └── commands/
│   │       └── seed_form_settings.py # Seed initial form settings
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py                     # Admin panel configuration
│   ├── models.py                    # FormSettings, FormSettingsHistory
│   ├── serializers.py               # Settings serializers
│   ├── views.py                     # Settings views
│   ├── urls.py                      # Settings endpoints
│   └── tests.py                     # Unit tests
│
├── media/                           # Uploaded files (payment proofs, etc.)
├── refs/                            # Reference documentation
│   ├── api_endpoints.md             # Detailed API documentation
│   ├── form_settings_api.md         # Form settings API docs
│   └── registration_form_fields.md  # Registration form field reference
│
├── .env                             # Environment variables (not in git)
├── .gitignore
├── manage.py
├── requirements.txt                 # Python dependencies
├── test_api.py                      # Integration test script
└── README.md                        # This file
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
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate

# Mac/Linux:
source .venv/bin/activate
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

# CORS (optional - defaults to localhost:3000)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Allowed Hosts (optional - defaults to localhost)
ALLOWED_HOSTS=localhost,127.0.0.1

# JWT Settings (in minutes)
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440
```

### 2. Production Configuration

For production, update the following:
```env
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
```

---

## 🗄️ Database Setup

### 1. Create MySQL Database
```sql
CREATE DATABASE db_alumni_reg CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. Quick Setup (Recommended)
```bash
# Run all migrations and seed data with a single command
python manage.py setup_db
```

This command will:
- Run all database migrations
- Seed initial form settings

**Options:**
```bash
# Include mock test data (for development only)
python manage.py setup_db --with-mock-data

# Skip migrations (if already applied)
python manage.py setup_db --skip-migrations

# Skip seeding (if already seeded)
python manage.py setup_db --skip-seeds
```

### 3. Manual Setup (Alternative)
If you prefer to run steps individually:
```bash
# Apply migrations
python manage.py migrate

# Seed initial form settings
python manage.py seed_form_settings

# (Optional) Generate mock test data for development
python manage.py seed_mock_data
```

### 4. Create Superuser (Admin Account)
```bash
python manage.py createsuperuser
```

Follow the prompts:
- Username: `admin@example.com` (use email as username)
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
http://localhost:8000/api/v1
```

### Authentication

Most endpoints require a JWT token. Include it in the header:
```
Authorization: Bearer YOUR_TOKEN_HERE
```

### Endpoint Categories

#### 1. **Authentication** (`/api/v1/auth/`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/login/` | Admin login |
| POST | `/logout/` | Admin logout (blacklists token) |
| POST | `/refresh/` | Refresh access token |
| GET | `/verify/` | Verify token validity |
| GET | `/admins/` | List all admin users 🔒 |
| POST | `/admins/` | Create new admin 🔒 |
| GET | `/admins/<id>/` | Get admin details 🔒 |
| PUT | `/admins/<id>/` | Update admin 🔒 |
| DELETE | `/admins/<id>/` | Deactivate admin 🔒 |
| POST | `/admins/<id>/reactivate/` | Reactivate admin 🔒 |
| GET | `/admins/<id>/activity/` | Get admin activity log 🔒 |

#### 2. **Registration** (`/api/v1/registration/`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/submit/` | Submit new registration (public) |
| GET | `/check-email/` | Check email availability (public) |

#### 3. **Form Settings**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/public/form-settings/` | Get public form settings (payment info) |
| GET | `/api/v1/admin/settings/form/` | Get/update form settings 🔒 |
| PUT | `/api/v1/admin/settings/form/` | Update form settings 🔒 |

#### 4. **Alumni Verification** (`/api/v1/verification/alumni/`) 🔒
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List pending alumni verifications |
| GET | `/<id>/` | Get application details |
| POST | `/<id>/verify/` | Verify as alumni |
| POST | `/<id>/reject/` | Reject application |
| GET | `/export/` | Export to CSV |

#### 5. **Payment Verification** (`/api/v1/verification/payment/`) 🔒
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List pending payment verifications |
| GET | `/<id>/` | Get application details |
| POST | `/<id>/confirm/` | Confirm payment |
| POST | `/<id>/reject/` | Reject application |
| GET | `/export/` | Export to CSV |

#### 6. **Rejected Applicants** (`/api/v1/rejected/`) 🔒
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all rejected applicants |
| GET | `/<id>/` | Get rejected applicant details |
| GET | `/export/` | Export to CSV |

#### 7. **Members** (`/api/v1/members/`) 🔒
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all approved members |
| GET | `/<id>/` | Get member details |
| POST | `/<id>/revoke/` | Revoke membership |
| POST | `/<id>/reinstate/` | Reinstate membership |
| GET | `/export/` | Export to CSV |

#### 8. **Dashboard** (`/api/v1/dashboard/`) 🔒
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/stats/` | Get statistics |
| GET | `/activity/` | Get recent activity |
| GET | `/filters/` | Get filter options |

🔒 = Requires authentication

### Request/Response Format

All API responses follow a consistent format:

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
curl -X POST http://localhost:8000/api/v1/registration/submit/ \
  -H "Content-Type: application/json" \
  -d '{
    "personalDetails": {
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
      "campus": "UP Cebu",
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
      "paymentMethod": "cash",
      "cashPaymentDate": "2026-01-24",
      "cashReceivedBy": "Admin Staff"
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
    "submittedAt": "2026-01-24T10:30:00Z"
  }
}
```

---

## 🧪 Testing

### Run Django Tests
```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test applications
python manage.py test accounts
python manage.py test members
python manage.py test form_settings

# Run with verbosity
python manage.py test --verbosity=2
```

### Integration Test Script

Test all API endpoints with the integration script:
```bash
python test_api.py
```

**Before running, ensure:**
1. The server is running (`python manage.py runserver`)
2. A superuser exists
3. Update credentials in `test_api.py` if needed:
```python
login_data = {
    "email": "admin@example.com",      # Your admin email
    "password": "your_password_here"   # Your admin password
}
```

---

## 📁 Reference Documentation

Detailed API documentation is available in the `refs/` directory:

- **[api_endpoints.md](refs/api_endpoints.md)** - Complete API documentation
- **[form_settings_api.md](refs/form_settings_api.md)** - Form settings API reference
- **[registration_form_fields.md](refs/registration_form_fields.md)** - Registration form field specifications

---

## 🔧 Management Commands

| Command | Description |
|---------|-------------|
| `python manage.py setup_db` | Run migrations and seed all data |
| `python manage.py seed_form_settings` | Seed initial form settings |
| `python manage.py seed_mock_data` | Generate mock test data |
| `python manage.py createsuperuser` | Create admin user |
| `python manage.py test` | Run all tests |

---

## 📅 Changelog

### Version 1.1.0 (2026-01-24)
- Added unified `setup_db` command for easier deployment
- Separated seeders from migrations
- Made settings production-ready (configurable via environment)
- Added comprehensive tests for form_settings
- Updated API endpoints documentation

### Version 1.0.0 (2025-01-03)
- Initial release
- Complete two-step verification system
- JWT authentication with token refresh
- CSV export functionality
- Admin management system
- Form settings management
