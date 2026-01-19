# Alumni Registration API - Endpoint Reference

**Base URL:** `http://localhost:8000/api/v1`

---

## Changelog

### 2026-01-19

**Schema Updates**

- Removed `title` field from `personalDetails` in registration and all response objects
- Added `middleName` field to `personalDetails`
- Consolidated migrations into single initial migration file
- Updated media file storage: payment proofs now stored at `/media/payment/gcash/` and `/media/payment/bank/`
- **Reapplication Rules**: Rejected applicants can now reapply with the same email; revoked members cannot
- **Security**: Email validation and check-email endpoint now use generic error messages to prevent email enumeration attacks
- **Campus Field**: `campus` is now a required field in `academicStatus` with default value "UP Cebu"

**Form Settings Endpoints (NEW)**

- Added `GET /admin/settings/form/` - Retrieve form settings (admin)
- Added `PUT /admin/settings/form/` - Update form settings (admin)
- Added `GET /public/form-settings/` - Retrieve public form settings (no auth required)
- New `FormSettings` model with JSON fields for payment accounts (GCash, Bank, Cash)
- New `FormSettingsHistory` model for tracking detailed changes
- Added `form_settings_updated` action to `AdminActivityLog`

**Member Detail Response Updates**

- Added `mentorship` section to `GET /members/<id>/` response with all mentorship program fields
- Expanded `membership` section to include full payment details (reference numbers, proof of payment URLs, etc.)

**New Filter Parameters**

Added the following filter parameters to all verification and member list endpoints:

| Parameter        | Type    | Description                                       |
| ---------------- | ------- | ------------------------------------------------- |
| `campus`         | string  | Filter by campus (exact match)                    |
| `province`       | string  | Filter by province (partial match)                |
| `mentorship`     | boolean | Filter by mentorship interest (`true` or `false`) |
| `payment_method` | string  | Filter by payment method: `gcash`, `bank`, `cash` |

**Updated Endpoints with New Filters:**

- `GET /verification/alumni/`
- `GET /verification/payment/`
- `GET /rejected/`
- `GET /members/`

**Dashboard Filters Response Updated:**

- Added `paymentMethods` to `/dashboard/filters/` response

### 2026-01-09

**Admin Activity Tracking & Management Enhancements**

- Added `POST /auth/admins/<id>/reactivate/` - Reactivate deactivated admin users
- Added `GET /auth/admins/<id>/activity/` - View admin activity logs with filtering, sorting, and pagination
- Enhanced `GET /dashboard/activity/` - Now shows comprehensive system activities including approvals, rejections, revocations, and admin management actions
- Added activity logging to all admin actions (login, logout, verifications, approvals, rejections, member management, admin deactivation/reactivation)

### 2026-01-08

**Dynamic Table Features & Member Management**

- Implemented pagination, filtering, and sorting for all list endpoints
- Added `POST /members/<id>/revoke/` - Revoke member's membership
- Added `POST /members/<id>/reinstate/` - Reinstate revoked membership

### 2026-01-06

**Initial Release**

- Authentication endpoints (login, logout, token verification)
- Registration submission and email checking
- Alumni and payment verification workflows
- Admin management CRUD operations
- Member listing and details
- Dashboard statistics and activity feed

---

## Authentication

All protected endpoints (🔒) require a JWT token in the header:

```
Authorization: Bearer YOUR_TOKEN_HERE
```

---

## Media Files (Payment Proofs)

Payment proof images uploaded during registration are accessible via the `/media/` URL path.

**Base Media URL:** `http://localhost:8000/media/`

### Storage Locations

| Payment Method | Storage Path            | Full URL Example                                         |
| -------------- | ----------------------- | -------------------------------------------------------- |
| GCash          | `/media/payment/gcash/` | `http://localhost:8000/media/payment/gcash/filename.jpg` |
| Bank Transfer  | `/media/payment/bank/`  | `http://localhost:8000/media/payment/bank/filename.jpg`  |

### Accessing Payment Proofs

When retrieving application details via `GET /verification/alumni/<id>/` or `GET /verification/payment/<id>/`, the response includes the full URL path to the payment proof in the `membership` object:

```json
{
  "membership": {
    "paymentMethod": "gcash",
    "gcashReferenceNumber": "2025010612345",
    "gcashProofOfPayment": "/media/payment/gcash/proof_12345.jpg",
    ...
  }
}
```

To display the image, prepend the base URL: `http://localhost:8000/media/payment/gcash/proof_12345.jpg`

> [!NOTE]
> Media files are served directly by Django in development. In production, configure your web server (nginx/Apache) to serve files from the `/media/` directory.

---

## 1. Authentication Endpoints

### `POST /auth/login/`

**Public** - Admin login

#### Request Body

| Field      | Type   | Required | Description         |
| ---------- | ------ | -------- | ------------------- |
| `email`    | string | ✅       | Admin email address |
| `password` | string | ✅       | Admin password      |

#### Example Request

```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "secretpassword"
  }'
```

#### Example Response (Success)

```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "email": "admin@example.com",
      "firstName": "Admin",
      "lastName": "User"
    }
  }
}
```

---

### `POST /auth/logout/` 🔒

**Protected** - Admin logout

#### Request Body

| Field     | Type   | Required | Description                |
| --------- | ------ | -------- | -------------------------- |
| `refresh` | string | ❌       | Refresh token to blacklist |

#### Example Request

```bash
curl -X POST http://localhost:8000/api/v1/auth/logout/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

#### Example Response

```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

### `GET /auth/verify/` 🔒

**Protected** - Verify token validity

#### Example Request

```bash
curl -X GET http://localhost:8000/api/v1/auth/verify/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Example Response

```json
{
  "success": true,
  "data": {
    "valid": true,
    "user": {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "first_name": "Admin",
      "last_name": "User"
    }
  }
}
```

---

## 2. Registration Endpoints (Public)

### `POST /registration/submit/`

**Public** - Submit new alumni registration with payment details and optional mentorship enrollment

#### Request Body Structure (multipart/form-data)

```json
{
  "personalDetails": {
    "firstName": "string",
    "middleName": "string (optional)",
    "lastName": "string",
    "suffix": "string (optional)",
    "maidenName": "string (optional)",
    "dateOfBirth": "YYYY-MM-DD",
    "email": "string (not @up.edu.ph)",
    "mobileNumber": "string (09XXXXXXXXX or +639XXXXXXXXX)",
    "currentAddress": "string",
    "province": "string (state/province code)",
    "city": "string (city/municipality code)",
    "barangay": "string (barangay code)",
    "zipCode": "string (4-digit)"
  },
  "academicStatus": {
    "campus": "string (default: UP Cebu)",
    "degreeProgram": "string",
    "yearGraduated": "YYYY (optional)",
    "studentNumber": "string (optional)"
  },
  "professional": {
    "currentEmployer": "string (optional)",
    "jobTitle": "string (optional)",
    "industry": "string (optional)",
    "yearsOfExperience": "string (optional)"
  },
  "membership": {
    "paymentMethod": "string (gcash, bank, cash)",
    "gcashReferenceNumber": "string (required if paymentMethod=gcash)",
    "bankName": "string (required if paymentMethod=bank)",
    "bankAccountNumber": "string (required if paymentMethod=bank)",
    "bankReferenceNumber": "string (required if paymentMethod=bank)",
    "bankSenderName": "string (required if paymentMethod=bank)",
    "cashPaymentDate": "YYYY-MM-DD (required if paymentMethod=cash)",
    "cashReceivedBy": "string (required if paymentMethod=cash)",
    "paymentNotes": "string (optional)"
  },
  "mentorship": {
    "joinMentorshipProgram": "boolean",
    "mentorshipAreas": ["string array - mentorship areas of interest"],
    "mentorshipAreasOther": "string (if other mentorship areas)",
    "mentorshipAvailability": "string (availability for mentorship)",
    "mentorshipFormat": "string (one-on-one, group, both)",
    "mentorshipIndustryTracks": ["string array - industry tracks"],
    "mentorshipIndustryTracksOther": "string (if other industry tracks)"
  },
  "gcashProofOfPayment": "file (required if paymentMethod=gcash)",
  "bankProofOfPayment": "file (required if paymentMethod=bank)"
}
```

#### Field Details

| Section         | Field                         | Type    | Required      | Validation                                      |
| --------------- | ----------------------------- | ------- | ------------- | ----------------------------------------------- |
| personalDetails | firstName                     | string  | ✅            | -                                               |
| personalDetails | middleName                    | string  | ❌            | -                                               |
| personalDetails | lastName                      | string  | ✅            | -                                               |
| personalDetails | suffix                        | string  | ❌            | -                                               |
| personalDetails | maidenName                    | string  | ❌            | -                                               |
| personalDetails | dateOfBirth                   | date    | ✅            | Format: YYYY-MM-DD                              |
| personalDetails | email                         | email   | ✅            | Must not end with @up.edu.ph, must be unique    |
| personalDetails | mobileNumber                  | string  | ✅            | Philippine format: 09XXXXXXXXX or +639XXXXXXXXX |
| personalDetails | currentAddress                | string  | ✅            | -                                               |
| personalDetails | province                      | string  | ✅            | Province/state code (e.g., "160200000")         |
| personalDetails | city                          | string  | ✅            | City/municipality code (e.g., "160206000")      |
| personalDetails | barangay                      | string  | ✅            | Barangay code (e.g., "160206004")               |
| personalDetails | zipCode                       | string  | ✅            | 4-digit zip code                                |
| academicStatus  | degreeProgram                 | string  | ✅            | Must exist in database                          |
| academicStatus  | campus                        | string  | ✅            | e.g., "UP Cebu"                                 |
| academicStatus  | yearGraduated                 | string  | ❌            | 4-digit year (optional)                         |
| academicStatus  | studentNumber                 | string  | ❌            | -                                               |
| professional    | currentEmployer               | string  | ❌            | -                                               |
| professional    | jobTitle                      | string  | ❌            | -                                               |
| professional    | industry                      | string  | ❌            | -                                               |
| professional    | yearsOfExperience             | string  | ❌            | -                                               |
| membership      | paymentMethod                 | string  | ✅            | One of: gcash, bank, cash                       |
| membership      | gcashReferenceNumber          | string  | ✅ (if gcash) | -                                               |
| membership      | bankName                      | string  | ✅ (if bank)  | -                                               |
| membership      | bankAccountNumber             | string  | ✅ (if bank)  | -                                               |
| membership      | bankReferenceNumber           | string  | ✅ (if bank)  | -                                               |
| membership      | bankSenderName                | string  | ✅ (if bank)  | -                                               |
| membership      | cashPaymentDate               | date    | ✅ (if cash)  | Format: YYYY-MM-DD                              |
| membership      | cashReceivedBy                | string  | ✅ (if cash)  | -                                               |
| mentorship      | joinMentorshipProgram         | boolean | ❌            | -                                               |
| mentorship      | mentorshipAreas               | array   | ❌            | Array of strings                                |
| mentorship      | mentorshipAreasOther          | string  | ❌            | -                                               |
| mentorship      | mentorshipAvailability        | string  | ❌            | -                                               |
| mentorship      | mentorshipFormat              | string  | ❌            | -                                               |
| mentorship      | mentorshipIndustryTracks      | array   | ❌            | Array of strings                                |
| mentorship      | mentorshipIndustryTracksOther | string  | ❌            | -                                               |
| files           | gcashProofOfPayment           | file    | ✅ (if gcash) | Image/PDF format                                |
| files           | bankProofOfPayment            | file    | ✅ (if bank)  | Image/PDF format                                |

#### Example Request (multipart/form-data)

```bash
curl -X POST http://localhost:8000/api/v1/registration/submit/ \
  -F "personalDetails={\"firstName\": \"Juan\", \"lastName\": \"Dela Cruz\", \"dateOfBirth\": \"1995-05-15\", \"email\": \"juan@example.com\", \"mobileNumber\": \"09171234567\", \"currentAddress\": \"123 Main St\", \"province\": \"160200000\", \"city\": \"160206000\", \"barangay\": \"160206004\"}" \
  -F "academicStatus={\"campus\": \"UP Cebu\", \"degreeProgram\": \"BS Comsci\", \"yearGraduated\": \"2020\", \"studentNumber\": \"2016-12345\"}" \
  -F "professional={\"currentEmployer\": \"Acme Corp\", \"jobTitle\": \"Software Developer\", \"industry\": \"Technology\", \"yearsOfExperience\": \"5\"}" \
  -F "membership={\"paymentMethod\": \"gcash\", \"gcashReferenceNumber\": \"2025010612345\"}" \
  -F "mentorship={\"joinMentorshipProgram\": true, \"mentorshipAreas\": [\"Career Development\", \"Technical Skills\"], \"mentorshipAvailability\": \"Weekends\", \"mentorshipFormat\": \"online\"}" \
  -F "gcashProofOfPayment=@/path/to/proof.jpg"
```

#### Example Response (Success - 201 Created)

```json
{
  "success": true,
  "message": "Registration submitted successfully",
  "data": {
    "applicationId": 1,
    "status": "pending_alumni_verification",
    "submittedAt": "2025-01-06T14:30:00Z"
  }
}
```

#### Example Response (Error - 400 Bad Request - Missing Payment Proof)

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "gcashProofOfPayment": ["Proof of payment is required for GCash"]
  }
}
```

#### Example Response (Error - 400 Bad Request - Bank Transfer)

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "membership": {
      "bankName": "bankName is required for bank transfer",
      "bankAccountNumber": "bankAccountNumber is required for bank transfer",
      "bankReferenceNumber": "bankReferenceNumber is required for bank transfer",
      "bankSenderName": "bankSenderName is required for bank transfer"
    },
    "bankProofOfPayment": ["Proof of payment is required for bank transfer"]
  }
}
```

"message": "Validation failed",
"errors": {
"personalDetails": {
"email": "Email already registered"
}
}
}

````

---

### `GET /registration/check-email/`
**Public** - Check email availability for registration

> [!IMPORTANT]
> **Security**: This endpoint returns generic responses without revealing specific reasons to prevent email enumeration attacks.

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `email` | string | ✅ | Email to check |

#### Example Request
```bash
curl "http://localhost:8000/api/v1/registration/check-email/?email=juan@example.com"
````

#### Example Response (Available)

```json
{
  "success": true,
  "data": {
    "available": true
  }
}
```

#### Example Response (Unavailable - Generic)

```json
{
  "success": true,
  "data": {
    "available": false
  }
}
```

> [!NOTE]
> The response does not reveal WHY the email is unavailable (already registered, revoked, or uses @up.edu.ph domain). Specific reasons are logged server-side for admin debugging.

---

## 3. Alumni Verification Endpoints 🔒

### `GET /verification/alumni/`

**Protected** - List pending alumni verifications

#### Query Parameters

| Parameter        | Type    | Required | Description                                                                                                                  |
| ---------------- | ------- | -------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `search`         | string  | ❌       | Search by name or email                                                                                                      |
| `page`           | integer | ❌       | Page number (default: 1)                                                                                                     |
| `limit`          | integer | ❌       | Items per page (default: 20, max: 100)                                                                                       |
| `ordering`       | string  | ❌       | Sort field. Options: `date_applied`, `first_name`, `last_name`, `email`. Prefix `-` for descending. Default: `-date_applied` |
| `date_from`      | date    | ❌       | Filter from date (YYYY-MM-DD) on date_applied                                                                                |
| `date_to`        | date    | ❌       | Filter to date (YYYY-MM-DD) on date_applied                                                                                  |
| `degree_program` | string  | ❌       | Filter by degree program name (partial match)                                                                                |
| `year_graduated` | string  | ❌       | Filter by graduation year (exact match)                                                                                      |
| `campus`         | string  | ❌       | Filter by campus (exact match)                                                                                               |
| `province`       | string  | ❌       | Filter by province (partial match)                                                                                           |
| `mentorship`     | boolean | ❌       | Filter by mentorship interest (`true` or `false`)                                                                            |
| `payment_method` | string  | ❌       | Filter by payment method: `gcash`, `bank`, or `cash`                                                                         |

#### Example Request

```bash
curl "http://localhost:8000/api/v1/verification/alumni/?search=juan&page=1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Example Response

```json
{
  "success": true,
  "data": {
    "applicants": [
      {
        "id": 1,
        "name": "Juan Dela Cruz",
        "email": "juan@example.com",
        "degreeProgram": "Bachelor of Science in Computer Science",
        "yearGraduated": "2020",
        "studentNumber": "2016-12345",
        "status": "pending_alumni_verification",
        "dateApplied": "2025-01-06T14:30:00Z"
      }
    ],
    "pagination": {
      "currentPage": 1,
      "totalPages": 1,
      "totalItems": 1,
      "limit": 20
    }
  }
}
```

---

### `GET /verification/alumni/<id>/`

**Protected** - Get application details for alumni verification

The response includes a `history` array showing the full application journey, including when the applicant registered.

#### Path Parameters

| Parameter | Type    | Description    |
| --------- | ------- | -------------- |
| `id`      | integer | Application ID |

#### Example Request

```bash
curl http://localhost:8000/api/v1/verification/alumni/1/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Example Response

```json
{
  "success": true,
  "data": {
    "id": 1,
    "status": "pending_alumni_verification",
    "dateApplied": "2025-01-06T14:30:00Z",
    "personalDetails": {
      "firstName": "Juan",
      "middleName": null,
      "lastName": "Dela Cruz",
      "suffix": null,
      "maidenName": null,
      "dateOfBirth": "1995-05-15",
      "email": "juan@example.com",
      "mobileNumber": "09171234567",
      "currentAddress": "123 Main St",
      "province": "Cebu",
      "city": "Cebu City",
      "barangay": "Lahug",
      "zipCode": "6000"
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
      "industry": "Technology",
      "yearsOfExperience": 5
    },
    "mentorship": {
      "joinMentorshipProgram": true,
      "mentorshipAreas": ["career-advancement", "technology-innovation"],
      "mentorshipAreasOther": null,
      "mentorshipIndustryTracks": ["it-software"],
      "mentorshipIndustryTracksOther": null,
      "mentorshipFormat": "both",
      "mentorshipAvailability": 8
    },
    "membership": {
      "paymentMethod": "gcash",
      "gcashReferenceNumber": "2025010612345",
      "gcashProofOfPayment": "/media/payment/gcash/proof_12345.jpg",
      "bankSenderName": null,
      "bankName": null,
      "bankAccountNumber": null,
      "bankReferenceNumber": null,
      "bankProofOfPayment": null,
      "cashPaymentDate": null,
      "cashReceivedBy": null,
      "paymentNotes": null
    },
    "history": [
      {
        "id": 1,
        "action": "submitted",
        "performedByName": "System",
        "notes": "Application submitted",
        "timestamp": "2025-01-06T14:30:00Z"
      }
    ]
  }
}
```

---

### `POST /verification/alumni/<id>/verify/`

**Protected** - Verify applicant as UP Cebu alumni

#### Path Parameters

| Parameter | Type    | Description    |
| --------- | ------- | -------------- |
| `id`      | integer | Application ID |

#### Request Body

| Field   | Type   | Required | Description |
| ------- | ------ | -------- | ----------- |
| `notes` | string | ❌       | Admin notes |

#### Example Request

```bash
curl -X POST http://localhost:8000/api/v1/verification/alumni/1/verify/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Verified via student records"
  }'
```

#### Example Response

```json
{
  "success": true,
  "message": "Applicant verified as alumni",
  "data": {
    "applicationId": 1,
    "status": "pending_payment_verification",
    "verifiedAt": "2025-01-06T15:00:00Z",
    "verifiedBy": "admin@example.com"
  }
}
```

---

### `POST /verification/alumni/<id>/reject/`

**Protected** - Reject application during alumni verification

#### Path Parameters

| Parameter | Type    | Description    |
| --------- | ------- | -------------- |
| `id`      | integer | Application ID |

#### Request Body

| Field    | Type   | Required | Description      |
| -------- | ------ | -------- | ---------------- |
| `reason` | string | ✅       | Rejection reason |

#### Example Request

```bash
curl -X POST http://localhost:8000/api/v1/verification/alumni/1/reject/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "No matching student record found"
  }'
```

#### Example Response

```json
{
  "success": true,
  "message": "Application rejected",
  "data": {
    "applicationId": 1,
    "status": "rejected",
    "rejectionStage": "alumni_verification",
    "rejectedAt": "2025-01-06T15:00:00Z",
    "reason": "No matching student record found"
  }
}
```

---

### `GET /verification/alumni/export/`

**Protected** - Export pending alumni verification list as CSV

#### Example Request

```bash
curl http://localhost:8000/api/v1/verification/alumni/export/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o pending_alumni_verification.csv
```

#### Response

Returns CSV file with columns: `ID, Name, Email, Degree Program, Year Graduated, Student Number, Date Applied`

---

## 4. Payment Verification Endpoints 🔒

### `GET /verification/payment/`

**Protected** - List pending payment verifications

#### Query Parameters

| Parameter        | Type    | Required | Description                                                                                                                              |
| ---------------- | ------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `search`         | string  | ❌       | Search by name or email                                                                                                                  |
| `page`           | integer | ❌       | Page number (default: 1)                                                                                                                 |
| `limit`          | integer | ❌       | Items per page (default: 20, max: 100)                                                                                                   |
| `ordering`       | string  | ❌       | Sort field. Options: `alumni_verified_at`, `first_name`, `last_name`, `email`. Prefix `-` for descending. Default: `-alumni_verified_at` |
| `date_from`      | date    | ❌       | Filter from date (YYYY-MM-DD) on date_applied                                                                                            |
| `date_to`        | date    | ❌       | Filter to date (YYYY-MM-DD) on date_applied                                                                                              |
| `degree_program` | string  | ❌       | Filter by degree program name (partial match)                                                                                            |
| `year_graduated` | string  | ❌       | Filter by graduation year (exact match)                                                                                                  |
| `campus`         | string  | ❌       | Filter by campus (exact match)                                                                                                           |
| `province`       | string  | ❌       | Filter by province (partial match)                                                                                                       |
| `mentorship`     | boolean | ❌       | Filter by mentorship interest (`true` or `false`)                                                                                        |
| `payment_method` | string  | ❌       | Filter by payment method: `gcash`, `bank`, or `cash`                                                                                     |

#### Example Request

```bash
curl "http://localhost:8000/api/v1/verification/payment/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Example Response

```json
{
  "success": true,
  "data": {
    "applicants": [
      {
        "id": 1,
        "name": "Juan Dela Cruz",
        "email": "juan@example.com",
        "paymentMethod": "gcash",
        "amount": 5000,
        "alumniVerifiedDate": "2025-01-06"
      }
    ],
    "pagination": {
      "currentPage": 1,
      "totalPages": 1,
      "totalItems": 1,
      "limit": 20
    }
  }
}
```

---

### `GET /verification/payment/<id>/`

**Protected** - Get application details for payment verification

#### Example Request

```bash
curl http://localhost:8000/api/v1/verification/payment/1/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Example Response

Same structure as alumni verification detail, with additional `amount` field. The `history` array shows the full application journey including when the applicant registered and when they were verified as alumni:

```json
{
  "success": true,
  "data": {
    "id": 1,
    "status": "pending_payment_verification",
    "dateApplied": "2025-01-06T14:30:00Z",
    "personalDetails": { ... },
    "academicStatus": { ... },
    "professional": { ... },
    "mentorship": { ... },
    "membership": { ... },
    "degreeProgramName": "Bachelor of Science in Computer Science",
    "alumniVerifiedAt": "2025-01-06T15:00:00Z",
    "approvedAt": null,
    "rejectedAt": null,
    "rejectionStage": null,
    "rejectionReason": null,
    "amount": 5000,
    "history": [
      {
        "id": 2,
        "action": "alumni_verified",
        "performedByName": "Admin User",
        "notes": "Verified from student records",
        "timestamp": "2025-01-06T15:00:00Z"
      },
      {
        "id": 1,
        "action": "submitted",
        "performedByName": "System",
        "notes": "Application submitted",
        "timestamp": "2025-01-06T14:30:00Z"
      }
    ]
  }
}
```

---

### `POST /verification/payment/<id>/confirm/`

**Protected** - Confirm payment and approve member

#### Path Parameters

| Parameter | Type    | Description    |
| --------- | ------- | -------------- |
| `id`      | integer | Application ID |

#### Request Body

| Field   | Type   | Required | Description |
| ------- | ------ | -------- | ----------- |
| `notes` | string | ❌       | Admin notes |

#### Example Request

```bash
curl -X POST http://localhost:8000/api/v1/verification/payment/1/confirm/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Payment verified via GCash transaction ref #12345"
  }'
```

#### Example Response

```json
{
  "success": true,
  "message": "Payment confirmed. Member approved.",
  "data": {
    "applicationId": 1,
    "memberId": 1,
    "status": "approved",
    "memberSince": "2025-01-06",
    "approvedAt": "2025-01-06T16:00:00Z"
  }
}
```

---

### `POST /verification/payment/<id>/reject/`

**Protected** - Reject application during payment verification

#### Request Body

| Field    | Type   | Required | Description      |
| -------- | ------ | -------- | ---------------- |
| `reason` | string | ✅       | Rejection reason |

#### Example Request

```bash
curl -X POST http://localhost:8000/api/v1/verification/payment/1/reject/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Payment not received"
  }'
```

#### Example Response

```json
{
  "success": true,
  "message": "Application rejected",
  "data": {
    "applicationId": 1,
    "status": "rejected",
    "rejectionStage": "payment_verification",
    "rejectedAt": "2025-01-06T16:00:00Z",
    "reason": "Payment not received"
  }
}
```

---

### `GET /verification/payment/export/`

**Protected** - Export pending payment verification list as CSV

Returns CSV file with columns: `ID, Name, Email, Payment Method, Alumni Verified Date`

---

## 5. Rejected Applicants Endpoints 🔒

### `GET /rejected/`

**Protected** - List all rejected applicants

#### Query Parameters

| Parameter         | Type    | Required | Description                                                                                                                |
| ----------------- | ------- | -------- | -------------------------------------------------------------------------------------------------------------------------- |
| `search`          | string  | ❌       | Search by name or email                                                                                                    |
| `rejection_stage` | string  | ❌       | Filter by stage: `alumni_verification` or `payment_verification`                                                           |
| `page`            | integer | ❌       | Page number (default: 1)                                                                                                   |
| `limit`           | integer | ❌       | Items per page (default: 20, max: 100)                                                                                     |
| `ordering`        | string  | ❌       | Sort field. Options: `rejected_at`, `first_name`, `last_name`, `email`. Prefix `-` for descending. Default: `-rejected_at` |
| `date_from`       | date    | ❌       | Filter from date (YYYY-MM-DD) on date_applied                                                                              |
| `date_to`         | date    | ❌       | Filter to date (YYYY-MM-DD) on date_applied                                                                                |
| `rejected_from`   | date    | ❌       | Filter from date (YYYY-MM-DD) on rejected_at                                                                               |
| `rejected_to`     | date    | ❌       | Filter to date (YYYY-MM-DD) on rejected_at                                                                                 |
| `degree_program`  | string  | ❌       | Filter by degree program name (partial match)                                                                              |
| `year_graduated`  | string  | ❌       | Filter by graduation year (exact match)                                                                                    |
| `campus`          | string  | ❌       | Filter by campus (exact match)                                                                                             |
| `province`        | string  | ❌       | Filter by province (partial match)                                                                                         |
| `mentorship`      | boolean | ❌       | Filter by mentorship interest (`true` or `false`)                                                                          |
| `payment_method`  | string  | ❌       | Filter by payment method: `gcash`, `bank`, or `cash`                                                                       |

#### Example Request

```bash
curl "http://localhost:8000/api/v1/rejected/?rejectionStage=alumni_verification" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Example Response

```json
{
  "success": true,
  "data": {
    "applicants": [
      {
        "id": 2,
        "name": "Jane Doe",
        "email": "jane@example.com",
        "rejectedAt": "2025-01-05",
        "rejectionStage": "Alumni Verification",
        "reason": "No matching student record"
      }
    ],
    "pagination": {
      "currentPage": 1,
      "totalPages": 1,
      "totalItems": 1,
      "limit": 20
    }
  }
}
```

---

### `GET /rejected/<id>/`

**Protected** - Get rejected applicant details

The response includes a `history` array showing the full application journey, including when the applicant registered, when they were verified (if applicable), and when they were rejected.

#### Example Request

```bash
curl http://localhost:8000/api/v1/rejected/2/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Example Response

```json
{
  "success": true,
  "data": {
    "id": 2,
    "status": "rejected",
    "dateApplied": "2026-01-15T10:30:00Z",
    "personalDetails": {
      "firstName": "Jane",
      "middleName": null,
      "lastName": "Doe",
      "suffix": null,
      "maidenName": null,
      "dateOfBirth": "1992-03-20",
      "email": "jane@example.com",
      "mobileNumber": "09181234567",
      "currentAddress": "456 Oak St",
      "province": "Cebu",
      "city": "Mandaue City",
      "barangay": "Basak",
      "zipCode": "6014"
    },
    "academicStatus": {
      "campus": "UP Cebu",
      "degreeProgram": "Bachelor of Arts in Communication",
      "yearGraduated": "2015",
      "studentNumber": null
    },
    "professional": {
      "currentEmployer": null,
      "jobTitle": null,
      "industry": null,
      "yearsOfExperience": null
    },
    "mentorship": {
      "joinMentorshipProgram": false,
      "mentorshipAreas": [],
      "mentorshipAreasOther": null,
      "mentorshipIndustryTracks": [],
      "mentorshipIndustryTracksOther": null,
      "mentorshipFormat": null,
      "mentorshipAvailability": null
    },
    "membership": {
      "paymentMethod": "gcash",
      "gcashReferenceNumber": "1234567890",
      "gcashProofOfPayment": "/media/payment/gcash/proof_123.jpg",
      "bankSenderName": null,
      "bankName": null,
      "bankAccountNumber": null,
      "bankReferenceNumber": null,
      "bankProofOfPayment": null,
      "cashPaymentDate": null,
      "cashReceivedBy": null,
      "paymentNotes": null
    },
    "degreeProgramName": "Bachelor of Arts in Communication",
    "alumniVerifiedAt": "2026-01-15T14:00:00Z",
    "approvedAt": null,
    "rejectedAt": "2026-01-16T09:30:00Z",
    "rejectionStage": "payment_verification",
    "rejectionReason": "Invalid payment proof - reference number does not match",
    "history": [
      {
        "id": 3,
        "action": "rejected",
        "performedByName": "Admin User",
        "notes": "Rejected: Invalid payment proof - reference number does not match",
        "timestamp": "2026-01-16T09:30:00Z"
      },
      {
        "id": 2,
        "action": "alumni_verified",
        "performedByName": "Admin User",
        "notes": "Verified from student records",
        "timestamp": "2026-01-15T14:00:00Z"
      },
      {
        "id": 1,
        "action": "submitted",
        "performedByName": "System",
        "notes": "Application submitted",
        "timestamp": "2026-01-15T10:30:00Z"
      }
    ]
  }
}
```

---

### `GET /rejected/export/`

**Protected** - Export rejected applicants list as CSV

Returns CSV file with columns: `ID, Name, Email, Rejection Stage, Reason, Rejected Date`

---

## 6. Members Endpoints 🔒

### `GET /members/`

**Protected** - List members

#### Query Parameters

| Parameter        | Type    | Required | Description                                                                                                    |
| ---------------- | ------- | -------- | -------------------------------------------------------------------------------------------------------------- |
| `search`         | string  | ❌       | Search by name or email                                                                                        |
| `status`         | string  | ❌       | Filter by status: `active`, `revoked`, or `all`. Default: `all`                                                |
| `page`           | integer | ❌       | Page number (default: 1)                                                                                       |
| `limit`          | integer | ❌       | Items per page (default: 20, max: 100)                                                                         |
| `ordering`       | string  | ❌       | Sort field. Options: `member_since`, `full_name`, `email`. Prefix `-` for descending. Default: `-member_since` |
| `date_from`      | date    | ❌       | Filter from date (YYYY-MM-DD) on member_since                                                                  |
| `date_to`        | date    | ❌       | Filter to date (YYYY-MM-DD) on member_since                                                                    |
| `degree_program` | string  | ❌       | Filter by degree program name (partial match)                                                                  |
| `year_graduated` | string  | ❌       | Filter by graduation year (exact match)                                                                        |
| `campus`         | string  | ❌       | Filter by campus (exact match)                                                                                 |
| `province`       | string  | ❌       | Filter by province (partial match)                                                                             |
| `mentorship`     | boolean | ❌       | Filter by mentorship interest (`true` or `false`)                                                              |
| `payment_method` | string  | ❌       | Filter by payment method: `gcash`, `bank`, or `cash`                                                           |

#### Example Request

```bash
curl "http://localhost:8000/api/v1/members/?search=juan" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Example Response

```json
{
  "success": true,
  "data": {
    "members": [
      {
        "id": 1,
        "fullName": "Juan Dela Cruz",
        "email": "juan@example.com",
        "degreeProgram": "Bachelor of Science in Computer Science",
        "yearGraduated": "2020",
        "memberSince": "2025-01-06",
        "isActive": true
      }
    ],
    "pagination": {
      "currentPage": 1,
      "totalPages": 1,
      "totalItems": 1,
      "limit": 20
    }
  }
}
```

---

### `GET /members/<id>/`

**Protected** - Get member details

#### Example Request

```bash
curl http://localhost:8000/api/v1/members/1/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Example Response

```json
{
  "success": true,
  "data": {
    "id": 1,
    "memberSince": "2026-01-08",
    "isActive": true,
    "personalDetails": {
      "firstName": "Juan",
      "middleName": null,
      "lastName": "Dela Cruz",
      "suffix": null,
      "maidenName": null,
      "email": "juan@example.com",
      "mobileNumber": "09171234567",
      "dateOfBirth": "1995-05-15",
      "currentAddress": "123 Main St",
      "province": "Cebu",
      "city": "Cebu City",
      "barangay": "Lahug",
      "zipCode": "6000"
    },
    "academicStatus": {
      "degreeProgram": "Bachelor of Science in Computer Science",
      "campus": "UP Cebu",
      "yearGraduated": "2020",
      "studentNumber": "2016-12345"
    },
    "professional": {
      "currentEmployer": "Acme Corp",
      "jobTitle": "Software Developer",
      "industry": "Technology",
      "yearsOfExperience": 5
    },
    "mentorship": {
      "joinMentorshipProgram": true,
      "mentorshipAreas": ["career-advancement", "technology-innovation"],
      "mentorshipAreasOther": null,
      "mentorshipIndustryTracks": ["it-software"],
      "mentorshipIndustryTracksOther": null,
      "mentorshipFormat": "one-on-one",
      "mentorshipAvailability": 4
    },
    "membership": {
      "paymentMethod": "gcash",
      "gcashReferenceNumber": "1234567890",
      "gcashProofOfPayment": "/media/payment/gcash/proof_12345.jpg",
      "bankSenderName": null,
      "bankName": null,
      "bankAccountNumber": null,
      "bankReferenceNumber": null,
      "bankProofOfPayment": null,
      "cashPaymentDate": null,
      "cashReceivedBy": null,
      "paymentNotes": null
    },
    "history": [
      {
        "id": 3,
        "action": "payment_confirmed",
        "performedByName": "Admin User",
        "notes": "Payment received",
        "timestamp": "2026-01-08T16:00:00Z"
      },
      {
        "id": 2,
        "action": "alumni_verified",
        "performedByName": "Admin User",
        "notes": "Verified via records",
        "timestamp": "2026-01-08T15:00:00Z"
      },
      {
        "id": 1,
        "action": "submitted",
        "performedByName": "System",
        "notes": "Application submitted",
        "timestamp": "2026-01-08T14:30:00Z"
      }
    ]
  }
}
```

---

### `PUT /members/<id>/update/`

**Protected** - Update member information

#### Request Body

```json
{
  "personalDetails": {
    "email": "newemail@example.com",
    "mobileNumber": "09181234567",
    "currentAddress": "456 New St"
  },
  "professional": {
    "currentEmployer": "New Company",
    "jobTitle": "Senior Developer",
    "industry": "Software"
  }
}
```

#### Updatable Fields

| Section         | Field           | Description       |
| --------------- | --------------- | ----------------- |
| personalDetails | email           | New email address |
| personalDetails | mobileNumber    | New mobile number |
| personalDetails | currentAddress  | New address       |
| professional    | currentEmployer | New employer      |
| professional    | jobTitle        | New job title     |
| professional    | industry        | New industry      |

#### Example Request

```bash
curl -X PUT http://localhost:8000/api/v1/members/1/update/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "professional": {
      "currentEmployer": "New Company Inc.",
      "jobTitle": "Senior Developer"
    }
  }'
```

#### Example Response

```json
{
  "success": true,
  "message": "Member updated successfully",
  "data": { ... }
}
```

---

### `POST /members/<id>/revoke/`

**Protected** - Revoke membership

Also accepts `DELETE` method.

#### Request Body

| Field    | Type   | Required | Description            |
| -------- | ------ | -------- | ---------------------- |
| `reason` | string | ✅       | Reason for revocation  |
| `notes`  | string | ❌       | Additional admin notes |

#### Example Request

```bash
curl -X POST http://localhost:8000/api/v1/members/1/revoke/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Non-payment of dues",
    "notes": "Multiple reminders sent"
  }'
```

#### Example Response

```json
{
  "success": true,
  "message": "Membership revoked successfully",
  "data": {
    "memberId": 1,
    "isActive": false,
    "revokedAt": "2026-01-09T12:30:00Z",
    "revokedBy": "admin@example.com",
    "reason": "Non-payment of dues"
  }
}
```

#### What Happens

1. Member's `is_active` is set to `false`
2. Application status changes to `revoked`
3. Audit entry is created in verification history

---

### `POST /members/<id>/reinstate/`

**Protected** - Reinstate a revoked membership

#### Request Body

| Field   | Type   | Required | Description                   |
| ------- | ------ | -------- | ----------------------------- |
| `notes` | string | ❌       | Admin notes for reinstatement |

#### Example Request

```bash
curl -X POST http://localhost:8000/api/v1/members/1/reinstate/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Payment received, membership restored"
  }'
```

#### Example Response

```json
{
  "success": true,
  "message": "Membership reinstated successfully",
  "data": {
    "memberId": 1,
    "isActive": true,
    "reinstatedAt": "2026-01-09T14:00:00Z",
    "reinstatedBy": "admin@example.com"
  }
}
```

#### What Happens

1. Member's `is_active` is set to `true`
2. Application status changes back to `approved`
3. Audit entry is created in verification history

---

### `GET /members/export/`

**Protected** - Export members list as CSV

Returns CSV file with columns: `ID, Name, Email, Degree Program, Year Graduated, Member Since, Active`

---

## 7. Dashboard Endpoints 🔒

### `GET /dashboard/stats/`

**Protected** - Get dashboard statistics

#### Example Request

```bash
curl http://localhost:8000/api/v1/dashboard/stats/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Example Response

```json
{
  "success": true,
  "data": {
    "stats": [
      { "label": "Pending Alumni Verification", "count": 5 },
      { "label": "Pending Payment Verification", "count": 3 },
      { "label": "Approved Members", "count": 150 }
    ]
  }
}
```

---

### `GET /dashboard/activity/`

**Protected** - Get recent system activities

> [!NOTE]
> **Enhanced in v2026-01-09**: Now combines activities from VerificationHistory and AdminActivityLog to show comprehensive system activity including approvals, rejections, revocations, and admin management actions.

#### Query Parameters

| Parameter | Type    | Required | Description                                  |
| --------- | ------- | -------- | -------------------------------------------- |
| `limit`   | integer | ❌       | Number of activities to return (default: 10) |

#### Example Request

```bash
curl "http://localhost:8000/api/v1/dashboard/activity/?limit=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Example Response

```json
{
  "success": true,
  "data": {
    "activities": [
      {
        "id": "al-45",
        "type": "Approved Member",
        "description": "Juan Dela Cruz",
        "performedBy": "admin@example.com",
        "timestamp": "2026-01-09 14:30:00",
        "notes": "Payment verified via GCash"
      },
      {
        "id": "vh-123",
        "type": "Alumni Verified",
        "description": "Maria Santos",
        "performedBy": "admin@example.com",
        "timestamp": "2026-01-09 13:15:00",
        "notes": "Verified from student records"
      },
      {
        "id": "al-44",
        "type": "Revoked Membership",
        "description": "Pedro Garcia",
        "performedBy": "admin@example.com",
        "timestamp": "2026-01-09 11:00:00",
        "notes": "Reason: Duplicate account"
      },
      {
        "id": "al-43",
        "type": "Reactivated Admin",
        "description": "staff@example.com",
        "performedBy": "admin@example.com",
        "timestamp": "2026-01-09 10:00:00",
        "notes": "Reactivating after review"
      }
    ]
  }
}
```

---

## Standard Response Format

### Success Response

```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... }
}
```

### Error Response

```json
{
  "success": false,
  "message": "Error message",
  "errors": { ... }
}
```

---

## Application Status Flow

```
┌──────────────────────────────┐
│  pending_alumni_verification │ ← Initial status after registration
└──────────────┬───────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
┌─────────────────────────────────┐     ┌──────────┐
│ pending_payment_verification    │     │ rejected │
│ (Alumni verified, awaiting pay) │     │ (Stage:  │
└──────────────┬──────────────────┘     │ alumni)  │
               │                        └──────────┘
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
┌──────────┐         ┌──────────┐
│ approved │         │ rejected │
│ (Member) │         │ (Stage:  │
└──────────┘         │ payment) │
                     └──────────┘
```

---

## HTTP Status Codes

| Code | Description                          |
| ---- | ------------------------------------ |
| 200  | OK - Request succeeded               |
| 201  | Created - Resource created           |
| 400  | Bad Request - Validation error       |
| 401  | Unauthorized - Missing/invalid token |
| 404  | Not Found - Resource doesn't exist   |
| 500  | Internal Server Error                |

---

## 8. Admin Management Endpoints 🔒

### `GET /auth/admins/`

**Protected** - List all admin users

#### Example Request

```bash
curl http://localhost:8000/api/v1/auth/admins/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Example Response

```json
{
  "success": true,
  "data": {
    "admins": [
      {
        "id": 1,
        "email": "admin@example.com",
        "first_name": "Admin",
        "last_name": "User",
        "is_active": true,
        "date_joined": "2025-01-06T10:00:00Z",
        "last_login": "2026-01-09T18:00:00Z"
      }
    ],
    "total": 1
  }
}
```

---

### `POST /auth/admins/`

**Protected** - Create a new admin

#### Request Body

| Field        | Type   | Required | Description                  |
| ------------ | ------ | -------- | ---------------------------- |
| `email`      | string | ✅       | Admin email (must be unique) |
| `password`   | string | ✅       | Password (min 8 characters)  |
| `first_name` | string | ❌       | First name                   |
| `last_name`  | string | ❌       | Last name                    |

#### Example Request

```bash
curl -X POST http://localhost:8000/api/v1/auth/admins/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newadmin@example.com",
    "password": "securepass123",
    "first_name": "New",
    "last_name": "Admin"
  }'
```

#### Example Response (201 Created)

```json
{
  "success": true,
  "message": "Admin created successfully",
  "data": {
    "id": 2,
    "email": "newadmin@example.com",
    "first_name": "New",
    "last_name": "Admin",
    "is_active": true,
    "date_joined": "2025-01-06T14:30:00Z",
    "last_login": null
  }
}
```

---

### `GET /auth/admins/<id>/`

**Protected** - Get admin details

#### Example Request

```bash
curl http://localhost:8000/api/v1/auth/admins/2/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Example Response

```json
{
  "success": true,
  "data": {
    "id": 2,
    "email": "newadmin@example.com",
    "first_name": "New",
    "last_name": "Admin",
    "is_active": true,
    "date_joined": "2025-01-06T14:30:00Z",
    "last_login": "2025-01-06T15:00:00Z"
  }
}
```

---

### `PUT /auth/admins/<id>/`

**Protected** - Update admin info

#### Request Body

All fields are optional:
| Field | Type | Description |
|-------|------|-------------|
| `email` | string | New email |
| `password` | string | New password |
| `first_name` | string | First name |
| `last_name` | string | Last name |

#### Example Request

```bash
curl -X PUT http://localhost:8000/api/v1/auth/admins/2/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Updated",
    "last_name": "Name"
  }'
```

#### Example Response

```json
{
  "success": true,
  "message": "Admin updated successfully",
  "data": {
    "id": 2,
    "email": "newadmin@example.com",
    "first_name": "Updated",
    "last_name": "Name",
    "is_active": true,
    "date_joined": "2025-01-06T14:30:00Z",
    "last_login": "2025-01-06T15:00:00Z"
  }
}
```

---

### `DELETE /auth/admins/<id>/`

**Protected** - Soft delete admin (deactivate)

This sets `is_active` to `false`. The admin record is preserved but they cannot login.

#### Example Request

```bash
curl -X DELETE http://localhost:8000/api/v1/auth/admins/2/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Example Response

```json
{
  "success": true,
  "message": "Admin deactivated successfully",
  "data": {
    "id": 2,
    "email": "newadmin@example.com",
    "isActive": false
  }
}
```

---

### `POST /auth/admins/<id>/reactivate/` 🔒

**Protected** - Reactivate a deactivated admin user

#### Path Parameters

| Parameter | Type    | Description   |
| --------- | ------- | ------------- |
| `id`      | integer | Admin user ID |

#### Request Body

| Field   | Type   | Required | Description                       |
| ------- | ------ | -------- | --------------------------------- |
| `notes` | string | ❌       | Optional notes about reactivation |

#### Example Request

```bash
curl -X POST http://localhost:8000/api/v1/auth/admins/1/reactivate/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Reactivating after review"
  }'
```

#### Example Response

```json
{
  "success": true,
  "message": "Admin reactivated successfully",
  "data": {
    "id": 1,
    "email": "admin@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true,
    "date_joined": "2026-01-01T10:00:00Z",
    "last_login": "2026-01-08T14:30:00Z"
  }
}
```

---

### `GET /auth/admins/<id>/activity/` 🔒

**Protected** - Get activity log for a specific admin

View all activities performed by a specific admin user.

#### Path Parameters

| Parameter | Type    | Description   |
| --------- | ------- | ------------- |
| `id`      | integer | Admin user ID |

#### Query Parameters

| Parameter     | Type     | Required | Description                                        |
| ------------- | -------- | -------- | -------------------------------------------------- |
| `date_from`   | datetime | ❌       | Filter from date (YYYY-MM-DD)                      |
| `date_to`     | datetime | ❌       | Filter to date (YYYY-MM-DD)                        |
| `action`      | string   | ❌       | Filter by action type                              |
| `target_type` | string   | ❌       | Filter by target type (application, member, admin) |
| `ordering`    | string   | ❌       | Sort field. Default: `-timestamp`                  |
| `page`        | integer  | ❌       | Page number (default: 1)                           |
| `limit`       | integer  | ❌       | Items per page (default: 20, max: 100)             |

**Available Actions:**

- `login`, `logout`
- `verify_alumni`, `reject_alumni`
- `approve_member`, `reject_payment`
- `revoke_member`, `reinstate_member`
- `deactivate_admin`, `reactivate_admin`

#### Example Request

```bash
curl "http://localhost:8000/api/v1/auth/admins/1/activity/?date_from=2026-01-01&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Example Response

```json
{
  "success": true,
  "data": {
    "activities": [
      {
        "id": 123,
        "action": "verify_alumni",
        "actionDisplay": "Verified Alumni",
        "timestamp": "2026-01-09T10:30:00Z",
        "targetType": "application",
        "targetId": 45,
        "targetName": "Juan Dela Cruz",
        "notes": "Verified from student records",
        "ipAddress": "192.168.1.1"
      },
      {
        "id": 122,
        "action": "login",
        "actionDisplay": "Login",
        "timestamp": "2026-01-09T09:00:00Z",
        "targetType": null,
        "targetId": null,
        "targetName": "",
        "notes": "",
        "ipAddress": "192.168.1.1"
      }
    ],
    "pagination": {
      "currentPage": 1,
      "totalPages": 1,
      "totalItems": 2
    }
  }
}
```

---

## 9. Filter Options Endpoint 🔒

### `GET /dashboard/filters/`

**Protected** - Get available filter options for dropdowns

Returns available degree programs, campuses, graduation years, and rejection stages to populate filter dropdowns.

#### Example Request

```bash
curl http://localhost:8000/api/v1/dashboard/filters/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Example Response

```json
{
  "success": true,
  "data": {
    "degreePrograms": [
      "Bachelor of Arts in Communication",
      "Bachelor of Science in Computer Science"
    ],
    "campuses": ["UP Cebu", "University of the Philippines Cebu"],
    "years": ["2024", "2023", "2022", "2021", "2020"],
    "rejectionStages": [
      { "value": "alumni_verification", "label": "Alumni Verification" },
      { "value": "payment_verification", "label": "Payment Verification" }
    ],
    "paymentMethods": [
      { "value": "gcash", "label": "GCash" },
      { "value": "bank", "label": "Bank Transfer" },
      { "value": "cash", "label": "Cash" }
    ]
  }
}
```

---

## 10. Form Settings Endpoints

Endpoints for managing dynamic payment information and registration form settings. Admins can configure membership fees, payment accounts (GCash, Bank, Cash), and success page messages.

### `GET /admin/settings/form/` 🔒

**Protected** - Retrieve current form settings with metadata

Returns the complete form settings including payment accounts, membership fee, success message, and last update information.

#### Example Request

```bash
curl http://localhost:8000/api/v1/admin/settings/form/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Example Response

```json
{
  "success": true,
  "data": {
    "settings": {
      "membershipFee": 1450.0,
      "paymentSettings": {
        "gcashAccounts": [
          {
            "name": "Juan Dela Cruz",
            "number": "09171234567"
          }
        ],
        "bankAccounts": [
          {
            "bankName": "BDO",
            "accountName": "UP Alumni Association",
            "accountNumber": "001234567890"
          }
        ],
        "cashPayment": {
          "address": "Lahug, Cebu City",
          "building": "UP Cebu Main Building",
          "office": "Room 101, Alumni Office",
          "openDays": ["mon", "tue", "wed", "thu", "fri"],
          "openHours": "8:00 AM - 5:00 PM"
        }
      },
      "successMessage": "Welcome to the UP Alumni Association - Cebu Chapter!"
    },
    "lastUpdated": {
      "at": "2026-01-19T14:30:00Z",
      "by": {
        "id": 1,
        "name": "Admin Name",
        "email": "admin@example.com"
      }
    }
  }
}
```

---

### `PUT /admin/settings/form/` 🔒

**Protected** - Update form settings

Update membership fee, payment accounts, and success message. Changes are logged to both `AdminActivityLog` and `FormSettingsHistory`.

> [!IMPORTANT]
> This endpoint requires the **complete settings object** to be sent. Partial updates are not supported. Fetch the current settings first using `GET /admin/settings/form/`, modify the desired fields, then send the entire object back.

#### Request Body

| Field                                          | Type     | Required | Description                                                |
| ---------------------------------------------- | -------- | -------- | ---------------------------------------------------------- |
| `membershipFee`                                | decimal  | ✅       | Membership fee amount (min: 0)                             |
| `paymentSettings`                              | object   | ✅       | Payment configuration object                               |
| `paymentSettings.gcashAccounts`                | array    | ❌       | List of GCash accounts (default: `[]`)                     |
| `paymentSettings.gcashAccounts[].name`         | string   | ✅       | Account holder name (max 255 chars)                        |
| `paymentSettings.gcashAccounts[].number`       | string   | ✅       | GCash number (11 digits, starts with 09)                   |
| `paymentSettings.bankAccounts`                 | array    | ❌       | List of bank accounts (default: `[]`)                      |
| `paymentSettings.bankAccounts[].bankName`      | string   | ✅       | Bank name (max 255 chars)                                  |
| `paymentSettings.bankAccounts[].accountName`   | string   | ✅       | Account holder name (max 255 chars)                        |
| `paymentSettings.bankAccounts[].accountNumber` | string   | ✅       | Account number (max 255 chars)                             |
| `paymentSettings.cashPayment`                  | object   | ❌       | Cash payment details (default: empty object)               |
| `paymentSettings.cashPayment.address`          | string   | ❌       | Office address (max 255 chars)                             |
| `paymentSettings.cashPayment.building`         | string   | ❌       | Building name (max 255 chars)                              |
| `paymentSettings.cashPayment.office`           | string   | ❌       | Office location (max 255 chars)                            |
| `paymentSettings.cashPayment.openDays`         | string[] | ❌       | Open days: `mon`, `tue`, `wed`, `thu`, `fri`, `sat`, `sun` |
| `paymentSettings.cashPayment.openHours`        | string   | ❌       | Office hours (max 100 chars)                               |
| `successMessage`                               | string   | ❌       | Success page message (max 500 chars, default: `""`)        |

#### Minimum Required Structure

The minimum valid request body must include `membershipFee` and `paymentSettings`:

```json
{
  "membershipFee": 1450.0,
  "paymentSettings": {}
}
```

#### Example Request (Adding GCash Account Only)

```bash
curl -X PUT http://localhost:8000/api/v1/admin/settings/form/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "membershipFee": 1450.00,
    "paymentSettings": {
      "gcashAccounts": [
        {
          "name": "Juan Dela Cruz",
          "number": "09171234567"
        }
      ]
    }
  }'
```

#### Example Request (Complete Structure)

```bash
curl -X PUT http://localhost:8000/api/v1/admin/settings/form/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "membershipFee": 1450.00,
    "paymentSettings": {
      "gcashAccounts": [
        {
          "name": "Juan Dela Cruz",
          "number": "09171234567"
        }
      ],
      "bankAccounts": [
        {
          "bankName": "BDO",
          "accountName": "UP Alumni Association",
          "accountNumber": "001234567890"
        }
      ],
      "cashPayment": {
        "address": "Lahug, Cebu City",
        "building": "UP Cebu Main Building",
        "office": "Room 101, Alumni Office",
        "openDays": ["mon", "tue", "wed", "thu", "fri"],
        "openHours": "8:00 AM - 5:00 PM"
      }
    },
    "successMessage": "Welcome to the UP Alumni Association - Cebu Chapter!"
  }'
```

#### Example Response (Success)

```json
{
  "success": true,
  "message": "Form settings updated successfully",
  "data": {
    "settings": {
      "membershipFee": 1450.0,
      "paymentSettings": {
        "gcashAccounts": [
          {
            "name": "Juan Dela Cruz",
            "number": "09171234567"
          }
        ],
        "bankAccounts": [
          {
            "bankName": "BDO",
            "accountName": "UP Alumni Association",
            "accountNumber": "001234567890"
          }
        ],
        "cashPayment": {
          "address": "Lahug, Cebu City",
          "building": "UP Cebu Main Building",
          "office": "Room 101, Alumni Office",
          "openDays": ["mon", "tue", "wed", "thu", "fri"],
          "openHours": "8:00 AM - 5:00 PM"
        }
      },
      "successMessage": "Welcome to the UP Alumni Association - Cebu Chapter!"
    },
    "lastUpdated": {
      "at": "2026-01-19T14:35:00Z",
      "by": {
        "id": 1,
        "name": "Admin Name",
        "email": "admin@example.com"
      }
    }
  }
}
```

#### Example Response (Validation Error)

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "membershipFee": ["Ensure this value is greater than or equal to 0."],
    "paymentSettings": {
      "gcashAccounts": [
        {
          "number": [
            "Invalid GCash number format. Must be 11 digits starting with 09."
          ]
        }
      ]
    },
    "successMessage": ["Ensure this field has no more than 500 characters."]
  }
}
```

---

### `GET /public/form-settings/`

**Public** - Retrieve form settings for registration form

Returns only the information needed for the public registration form. Does NOT include admin details, modification history, or sensitive metadata.

> [!NOTE]
> This endpoint does not require authentication and is intended for use by the public registration form.

#### Example Request

```bash
curl http://localhost:8000/api/v1/public/form-settings/
```

#### Example Response

```json
{
  "success": true,
  "data": {
    "membershipFee": 1450.0,
    "paymentMethods": {
      "gcash": {
        "accounts": [
          {
            "name": "Juan Dela Cruz",
            "number": "09171234567"
          }
        ]
      },
      "bank": {
        "accounts": [
          {
            "bankName": "BDO",
            "accountName": "UP Alumni Association",
            "accountNumber": "001234567890"
          }
        ]
      },
      "cash": {
        "address": "Lahug, Cebu City",
        "building": "UP Cebu Main Building",
        "office": "Room 101, Alumni Office",
        "openDays": ["mon", "tue", "wed", "thu", "fri"],
        "openHours": "8:00 AM - 5:00 PM"
      }
    },
    "successMessage": "Welcome to the UP Alumni Association - Cebu Chapter!"
  }
}
```

---

### Form Settings Data Types Reference

#### GCash Account Object

| Field    | Type   | Required | Validation                              |
| -------- | ------ | -------- | --------------------------------------- |
| `name`   | string | ✅       | Max 255 characters                      |
| `number` | string | ✅       | Exactly 11 digits, must start with `09` |

**Number Format Regex:** `^09[0-9]{9}$`

#### Bank Account Object

| Field           | Type   | Required | Validation         |
| --------------- | ------ | -------- | ------------------ |
| `bankName`      | string | ✅       | Max 255 characters |
| `accountName`   | string | ✅       | Max 255 characters |
| `accountNumber` | string | ✅       | Max 255 characters |

#### Cash Payment Object

| Field       | Type     | Required | Validation                                                |
| ----------- | -------- | -------- | --------------------------------------------------------- |
| `address`   | string   | ❌       | Max 255 characters                                        |
| `building`  | string   | ❌       | Max 255 characters                                        |
| `office`    | string   | ❌       | Max 255 characters                                        |
| `openDays`  | string[] | ❌       | Array of: `mon`, `tue`, `wed`, `thu`, `fri`, `sat`, `sun` |
| `openHours` | string   | ❌       | Max 100 characters (e.g., "8:00 AM - 5:00 PM")            |

#### Open Days Reference

| Value | Display Label |
| ----- | ------------- |
| `mon` | Monday        |
| `tue` | Tuesday       |
| `wed` | Wednesday     |
| `thu` | Thursday      |
| `fri` | Friday        |
| `sat` | Saturday      |
| `sun` | Sunday        |

---

### Activity Logging

When form settings are updated via `PUT /admin/settings/form/`, the following are logged:

1. **AdminActivityLog Entry:**
   - `action`: `form_settings_updated`
   - `actionDisplay`: `Updated Form Settings`
   - `targetType`: `form_settings`
   - `notes`: Human-readable summary of changes

2. **FormSettingsHistory Entry:**
   - Detailed JSON diff of what changed (from/to values)

#### Example Activity Log Notes

```
Changed membership fee from Php 500.00 to Php 1,450.00. Added 2 GCash account(s). Modified cash payment details: openDays, openHours.
```

---

## 11. Frontend Filter Implementation Guide

This section provides guidance for implementing filters in the frontend application.

### Filter Types Summary

| Filter            | Input Type                   | Backend Lookup | Notes                                         |
| ----------------- | ---------------------------- | -------------- | --------------------------------------------- |
| `search`          | Text input                   | `icontains`    | Searches name and email                       |
| `degree_program`  | Searchable autocomplete      | `icontains`    | Partial match, use API values for suggestions |
| `campus`          | Select dropdown              | `exact`        | Use predefined list (8 UP campuses)           |
| `year_graduated`  | Select dropdown              | `exact`        | Generate options from 1960 to current year    |
| `province`        | Searchable text/autocomplete | `icontains`    | Use external API for suggestions              |
| `mentorship`      | Toggle/Select (Yes/No/All)   | `exact`        | `true`, `false`, or omit for all              |
| `payment_method`  | Select dropdown              | `exact`        | `gcash`, `bank`, `cash`                       |
| `rejection_stage` | Select dropdown              | `exact`        | `alumni_verification`, `payment_verification` |
| `status`          | Select dropdown (Members)    | custom         | `active`, `revoked`, `all`                    |
| `date_from/to`    | Date picker                  | `gte`/`lte`    | Format: YYYY-MM-DD                            |

### Campus Options (Predefined)

```javascript
const campusOptions = [
  "UP Cebu",
  "UP Diliman",
  "UP Manila",
  "UP Los Baños",
  "UP Visayas",
  "UP Mindanao",
  "UP Baguio",
  "UP Open University",
];
```

### Year Graduated Options (Dynamic)

Generate dropdown options from 1960 to the current year:

```javascript
const currentYear = new Date().getFullYear();
const yearOptions = Array.from({ length: currentYear - 1960 + 1 }, (_, i) =>
  String(currentYear - i),
);
// Result: ["2026", "2025", "2024", ..., "1961", "1960"]
```

### Payment Method Options

```javascript
const paymentMethodOptions = [
  { value: "gcash", label: "GCash" },
  { value: "bank", label: "Bank Transfer" },
  { value: "cash", label: "Cash" },
];
```

### Mentorship Filter

```javascript
const mentorshipOptions = [
  { value: "", label: "All" }, // Omit parameter
  { value: "true", label: "Yes" },
  { value: "false", label: "No" },
];
```

### Example API Calls with Filters

```javascript
// Alumni verification with multiple filters
GET /api/v1/verification/alumni/?campus=UP%20Cebu&year_graduated=2020&mentorship=true&payment_method=gcash

// Members filtered by province and active status
GET /api/v1/members/?province=Cebu&status=active&ordering=-member_since

// Rejected applicants by stage and date range
GET /api/v1/rejected/?rejection_stage=payment_verification&rejected_from=2026-01-01&rejected_to=2026-01-31

// Search with pagination
GET /api/v1/verification/payment/?search=juan&page=1&limit=20
```

### Province Filter Implementation

The province filter uses a partial match (`icontains`), so you can:

1. Use an external Philippine address API for autocomplete suggestions
2. Pass the selected province name to the backend
3. The backend will match any records containing that text

```javascript
// Example: User selects "Cebu" from external API
GET /api/v1/members/?province=Cebu
// Matches: "Cebu", "Cebu City", "Metro Cebu", etc.
```

---

## Changelog

| Date       | Change                                                                                                                                                            |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-01-19 | **Form Settings Endpoints**: Added `GET/PUT /admin/settings/form/` (admin) and `GET /public/form-settings/` (public) for dynamic payment configuration            |
| 2026-01-19 | **New Models**: Added `FormSettings` (singleton) and `FormSettingsHistory` for settings management and audit trail                                                |
| 2026-01-19 | **Activity Log**: Added `form_settings_updated` action and `form_settings` target type to `AdminActivityLog`                                                      |
| 2026-01-09 | **Members Status Filter**: Added `status` query parameter to `/members/` endpoint to filter by `active`, `revoked`, or `all` (default)                            |
| 2026-01-09 | **Enhanced Revoke Endpoint**: `POST /members/<id>/revoke/` now requires a `reason` field, updates application status to `revoked`, and logs to audit trail        |
| 2026-01-09 | **New Reinstate Endpoint**: Added `POST /members/<id>/reinstate/` to reactivate revoked members with audit trail                                                  |
| 2026-01-09 | **New Application Status**: Added `revoked` status to distinguish from rejected applicants                                                                        |
| 2026-01-09 | **Member Model**: Added `revoked_at`, `revoked_by`, `revocation_reason`, `reinstated_at`, `reinstated_by` tracking fields                                         |
| 2026-01-08 | **Removed Address Endpoints**: `/registration/reference/provinces/`, `/cities/`, `/barangays/` endpoints removed - frontend uses external API                     |
| 2026-01-08 | **Address Fields**: Province, city, barangay now stored as free text strings instead of foreign keys                                                              |
| 2026-01-08 | **API Versioning**: All endpoints now use `/api/v1/` prefix for future-proofing                                                                                   |
| 2026-01-08 | **CamelCase Consistency**: All JSON responses now use camelCase (automatic conversion via `djangorestframework-camel-case`)                                       |
| 2026-01-08 | **Field Rename**: `degree` → `degreeProgram` for consistent naming across all endpoints                                                                           |
| 2026-01-08 | **Flatten Member Details**: `application_details` wrapper removed; `personalDetails`, `academicStatus`, `professional`, `membership`, `history` now at root level |
| 2026-01-08 | Added filtering, sorting, and pagination to all list endpoints                                                                                                    |
| 2026-01-08 | Added `/api/v1/dashboard/filters/` endpoint for filter dropdown options                                                                                           |
| 2026-01-06 | Removed `role` field from login response                                                                                                                          |
| 2026-01-06 | Removed `username` field - using email as identifier                                                                                                              |
| 2026-01-06 | Added admin management endpoints (list, create, get, update, soft-delete)                                                                                         |
