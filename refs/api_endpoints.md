# Alumni Registration API - Endpoint Reference

**Base URL:** `http://localhost:8000/api/v1`

---

## Changelog

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

## 1. Authentication Endpoints

### `POST /auth/login/`
**Public** - Admin login

#### Request Body
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | ✅ | Admin email address |
| `password` | string | ✅ | Admin password |

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
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `refresh` | string | ❌ | Refresh token to blacklist |

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
**Public** - Submit new alumni registration

#### Request Body Structure
```json
{
  "personalDetails": {
    "title": "string (Mr, Ms, Mrs, Dr)",
    "firstName": "string",
    "lastName": "string",
    "suffix": "string (optional)",
    "maidenName": "string (optional)",
    "dateOfBirth": "YYYY-MM-DD",
    "email": "string (not @up.edu.ph)",
    "mobileNumber": "string (09XXXXXXXXX or +639XXXXXXXXX)",
    "currentAddress": "string",
    "province": "string",
    "city": "string",
    "barangay": "string"
  },
  "academicStatus": {
    "degreeProgram": "string",
    "yearGraduated": "YYYY",
    "studentNumber": "string (optional)"
  },
  "professional": {
    "currentEmployer": "string (optional)",
    "jobTitle": "string (optional)",
    "industry": "string (optional)"
  },
  "membership": {
    "paymentMethod": "string (gcash, bank, cash)"
  }
}
```

#### Field Details

| Section | Field | Type | Required | Validation |
|---------|-------|------|----------|------------|
| personalDetails | title | string | ✅ | One of: Mr, Ms, Mrs, Dr |
| personalDetails | firstName | string | ✅ | - |
| personalDetails | lastName | string | ✅ | - |
| personalDetails | suffix | string | ❌ | - |
| personalDetails | maidenName | string | ❌ | - |
| personalDetails | dateOfBirth | date | ✅ | Format: YYYY-MM-DD |
| personalDetails | email | email | ✅ | Must not end with @up.edu.ph, must be unique |
| personalDetails | mobileNumber | string | ✅ | Philippine format: 09XXXXXXXXX or +639XXXXXXXXX |
| personalDetails | currentAddress | string | ✅ | - |
| personalDetails | province | string | ✅ | Free text (use external API for selection) |
| personalDetails | city | string | ✅ | Free text (use external API for selection) |
| personalDetails | barangay | string | ✅ | Free text (use external API for selection) |
| academicStatus | degreeProgram | string | ✅ | Must exist in database |
| academicStatus | yearGraduated | string | ✅ | 4-digit year |
| academicStatus | studentNumber | string | ❌ | - |
| professional | currentEmployer | string | ❌ | - |
| professional | jobTitle | string | ❌ | - |
| professional | industry | string | ❌ | - |
| membership | paymentMethod | string | ✅ | One of: gcash, bank, cash |

#### Example Request
```bash
curl -X POST http://localhost:8000/api/v1/registration/submit/ \
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

#### Example Response (Error - 400 Bad Request)
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "personalDetails": {
      "email": "Email already registered"
    }
  }
}
```

---

### `GET /registration/check-email/`
**Public** - Check email availability

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `email` | string | ✅ | Email to check |

#### Example Request
```bash
curl "http://localhost:8000/api/v1/registration/check-email/?email=juan@example.com"
```

#### Example Response
```json
{
  "success": true,
  "data": {
    "available": true,
    "message": "Email is available"
  }
}
```

---

## 3. Reference Data Endpoints (Public)

> [!NOTE]
> **Address Data**: Province, city, and barangay lookups have been moved to an external API. The frontend should use a third-party Philippine address API for address selection. Address fields are now stored as plain text strings.

### `GET /registration/reference/degree-programs/`
**Public** - List all active degree programs

#### Example Request
```bash
curl http://localhost:8000/api/v1/registration/reference/degree-programs/
```

#### Example Response
```json
{
  "success": true,
  "data": [
    { "id": 1, "name": "Bachelor of Science in Computer Science", "college": "College of Science" },
    { "id": 2, "name": "Bachelor of Arts in Communication", "college": "College of Social Sciences" }
  ]
}
```

---

## 4. Alumni Verification Endpoints 🔒

### `GET /verification/alumni/`
**Protected** - List pending alumni verifications

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `search` | string | ❌ | Search by name or email |
| `page` | integer | ❌ | Page number (default: 1) |
| `limit` | integer | ❌ | Items per page (default: 20, max: 100) |
| `ordering` | string | ❌ | Sort field. Options: `date_applied`, `first_name`, `last_name`, `email`. Prefix `-` for descending. Default: `-date_applied` |
| `date_from` | date | ❌ | Filter from date (YYYY-MM-DD) on date_applied |
| `date_to` | date | ❌ | Filter to date (YYYY-MM-DD) on date_applied |
| `degree_program` | string | ❌ | Filter by degree program name |
| `year_graduated` | string | ❌ | Filter by graduation year |

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
      "totalItems": 1
    }
  }
}
```

---

### `GET /verification/alumni/<id>/`
**Protected** - Get application details for alumni verification

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Application ID |

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
      "title": "Mr",
      "firstName": "Juan",
      "lastName": "Dela Cruz",
      "suffix": null,
      "maidenName": null,
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
| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Application ID |

#### Request Body
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `notes` | string | ❌ | Admin notes |

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
| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Application ID |

#### Request Body
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `reason` | string | ✅ | Rejection reason |

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

## 5. Payment Verification Endpoints 🔒

### `GET /verification/payment/`
**Protected** - List pending payment verifications

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `search` | string | ❌ | Search by name or email |
| `page` | integer | ❌ | Page number (default: 1) |
| `limit` | integer | ❌ | Items per page (default: 20, max: 100) |
| `ordering` | string | ❌ | Sort field. Options: `alumni_verified_at`, `first_name`, `last_name`, `email`. Prefix `-` for descending. Default: `-alumni_verified_at` |
| `date_from` | date | ❌ | Filter from date (YYYY-MM-DD) on date_applied |
| `date_to` | date | ❌ | Filter to date (YYYY-MM-DD) on date_applied |
| `degree_program` | string | ❌ | Filter by degree program name |
| `year_graduated` | string | ❌ | Filter by graduation year |

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
      "totalItems": 1
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
Same structure as alumni verification detail, with additional `amount` field.

---

### `POST /verification/payment/<id>/confirm/`
**Protected** - Confirm payment and approve member

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Application ID |

#### Request Body
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `notes` | string | ❌ | Admin notes |

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
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `reason` | string | ✅ | Rejection reason |

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

## 6. Rejected Applicants Endpoints 🔒

### `GET /rejected/`
**Protected** - List all rejected applicants

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `search` | string | ❌ | Search by name or email |
| `rejection_stage` | string | ❌ | Filter by stage: `alumni_verification` or `payment_verification` |
| `page` | integer | ❌ | Page number (default: 1) |
| `limit` | integer | ❌ | Items per page (default: 20, max: 100) |
| `ordering` | string | ❌ | Sort field. Options: `rejected_at`, `first_name`, `last_name`, `email`. Prefix `-` for descending. Default: `-rejected_at` |
| `date_from` | date | ❌ | Filter from date (YYYY-MM-DD) on date_applied |
| `date_to` | date | ❌ | Filter to date (YYYY-MM-DD) on date_applied |
| `rejected_from` | date | ❌ | Filter from date (YYYY-MM-DD) on rejected_at |
| `rejected_to` | date | ❌ | Filter to date (YYYY-MM-DD) on rejected_at |
| `degree_program` | string | ❌ | Filter by degree program name |
| `year_graduated` | string | ❌ | Filter by graduation year |

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
      "totalItems": 1
    }
  }
}
```

---

### `GET /rejected/<id>/`
**Protected** - Get rejected applicant details

#### Example Request
```bash
curl http://localhost:8000/api/v1/rejected/2/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### `GET /rejected/export/`
**Protected** - Export rejected applicants list as CSV

Returns CSV file with columns: `ID, Name, Email, Rejection Stage, Reason, Rejected Date`

---

## 7. Members Endpoints 🔒

### `GET /members/`
**Protected** - List members

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `search` | string | ❌ | Search by name or email |
| `status` | string | ❌ | Filter by status: `active`, `revoked`, or `all`. Default: `all` |
| `page` | integer | ❌ | Page number (default: 1) |
| `limit` | integer | ❌ | Items per page (default: 20, max: 100) |
| `ordering` | string | ❌ | Sort field. Options: `member_since`, `full_name`, `email`. Prefix `-` for descending. Default: `-member_since` |
| `date_from` | date | ❌ | Filter from date (YYYY-MM-DD) on member_since |
| `date_to` | date | ❌ | Filter to date (YYYY-MM-DD) on member_since |
| `degree_program` | string | ❌ | Filter by degree program name |
| `year_graduated` | string | ❌ | Filter by graduation year |

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
      "totalItems": 1
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
      "title": "Mr",
      "firstName": "Juan",
      "lastName": "Dela Cruz",
      "suffix": null,
      "email": "juan@example.com",
      "mobileNumber": "09171234567",
      "dateOfBirth": "1995-05-15",
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
| Section | Field | Description |
|---------|-------|-------------|
| personalDetails | email | New email address |
| personalDetails | mobileNumber | New mobile number |
| personalDetails | currentAddress | New address |
| professional | currentEmployer | New employer |
| professional | jobTitle | New job title |
| professional | industry | New industry |

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
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `reason` | string | ✅ | Reason for revocation |
| `notes` | string | ❌ | Additional admin notes |

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
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `notes` | string | ❌ | Admin notes for reinstatement |

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

## 8. Dashboard Endpoints 🔒

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
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | ❌ | Number of activities to return (default: 10) |
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

| Code | Description |
|------|-------------|
| 200 | OK - Request succeeded |
| 201 | Created - Resource created |
| 400 | Bad Request - Validation error |
| 401 | Unauthorized - Missing/invalid token |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Server Error |

---

## 9. Admin Management Endpoints 🔒

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
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | ✅ | Admin email (must be unique) |
| `password` | string | ✅ | Password (min 8 characters) |
| `first_name` | string | ❌ | First name |
| `last_name` | string | ❌ | Last name |

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
| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Admin user ID |

#### Request Body
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `notes` | string | ❌ | Optional notes about reactivation |

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
| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Admin user ID |

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `date_from` | datetime | ❌ | Filter from date (YYYY-MM-DD) |
| `date_to` | datetime | ❌ | Filter to date (YYYY-MM-DD) |
| `action` | string | ❌ | Filter by action type |
| `target_type` | string | ❌ | Filter by target type (application, member, admin) |
| `ordering` | string | ❌ | Sort field. Default: `-timestamp` |
| `page` | integer | ❌ | Page number (default: 1) |
| `limit` | integer | ❌ | Items per page (default: 20, max: 100) |

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

## 10. Filter Options Endpoint 🔒

### `GET /dashboard/filters/`
**Protected** - Get available filter options for dropdowns

Returns available degree programs, graduation years, and rejection stages to populate filter dropdowns.

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
    "years": ["2024", "2023", "2022", "2021", "2020"],
    "rejectionStages": [
      {"value": "alumni_verification", "label": "Alumni Verification"},
      {"value": "payment_verification", "label": "Payment Verification"}
    ]
  }
}
```

---

## Changelog

| Date | Change |
|------|--------|
| 2026-01-09 | **Members Status Filter**: Added `status` query parameter to `/members/` endpoint to filter by `active`, `revoked`, or `all` (default) |
| 2026-01-09 | **Enhanced Revoke Endpoint**: `POST /members/<id>/revoke/` now requires a `reason` field, updates application status to `revoked`, and logs to audit trail |
| 2026-01-09 | **New Reinstate Endpoint**: Added `POST /members/<id>/reinstate/` to reactivate revoked members with audit trail |
| 2026-01-09 | **New Application Status**: Added `revoked` status to distinguish from rejected applicants |
| 2026-01-09 | **Member Model**: Added `revoked_at`, `revoked_by`, `revocation_reason`, `reinstated_at`, `reinstated_by` tracking fields |
| 2026-01-08 | **Removed Address Endpoints**: `/registration/reference/provinces/`, `/cities/`, `/barangays/` endpoints removed - frontend uses external API |
| 2026-01-08 | **Address Fields**: Province, city, barangay now stored as free text strings instead of foreign keys |
| 2026-01-08 | **API Versioning**: All endpoints now use `/api/v1/` prefix for future-proofing |
| 2026-01-08 | **CamelCase Consistency**: All JSON responses now use camelCase (automatic conversion via `djangorestframework-camel-case`) |
| 2026-01-08 | **Field Rename**: `degree` → `degreeProgram` for consistent naming across all endpoints |
| 2026-01-08 | **Flatten Member Details**: `application_details` wrapper removed; `personalDetails`, `academicStatus`, `professional`, `membership`, `history` now at root level |
| 2026-01-08 | Added filtering, sorting, and pagination to all list endpoints |
| 2026-01-08 | Added `/api/v1/dashboard/filters/` endpoint for filter dropdown options |
| 2026-01-06 | Removed `role` field from login response |
| 2026-01-06 | Removed `username` field - using email as identifier |
| 2026-01-06 | Added admin management endpoints (list, create, get, update, soft-delete) |
