# Form Settings API Reference

Reference for backend endpoint and database schema design for the registration form settings.

---

## Overview

The Form Settings feature allows admins to configure:

1. Lifetime membership fee amount
2. Payment method details (GCash, Bank, Cash)
3. Success page custom message

All admins have access to view and modify these settings.

---

## Database Schema

### Option A: JSON Column Approach (Recommended for Simplicity)

MySQL supports JSON columns (since v5.7). This approach stores array data as JSON.

```sql
CREATE TABLE form_settings (
    id INT PRIMARY KEY DEFAULT 1,
    membership_fee DECIMAL(10, 2) NOT NULL DEFAULT 1450.00,
    gcash_accounts JSON DEFAULT '[]',
    bank_accounts JSON DEFAULT '[]',
    cash_payment JSON DEFAULT NULL,
    success_message VARCHAR(500) DEFAULT '',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT DEFAULT NULL,
    FOREIGN KEY (updated_by) REFERENCES admins(id) ON DELETE SET NULL,
    CONSTRAINT single_row CHECK (id = 1)
);
```

### Option B: Normalized Tables (Recommended for Strict Validation)

```sql
-- Main settings table
CREATE TABLE form_settings (
    id INT PRIMARY KEY DEFAULT 1,
    membership_fee DECIMAL(10, 2) NOT NULL DEFAULT 1450.00,
    cash_address VARCHAR(255) DEFAULT '',
    cash_building VARCHAR(255) DEFAULT '',
    cash_office VARCHAR(255) DEFAULT '',
    cash_open_days JSON DEFAULT '[]',
    cash_open_hours VARCHAR(100) DEFAULT '',
    success_message VARCHAR(500) DEFAULT '',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT DEFAULT NULL,
    FOREIGN KEY (updated_by) REFERENCES admins(id) ON DELETE SET NULL,
    CONSTRAINT single_row CHECK (id = 1)
);

-- GCash accounts table
CREATE TABLE form_settings_gcash_accounts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    number VARCHAR(11) NOT NULL,
    display_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT gcash_number_format CHECK (number REGEXP '^09[0-9]{9}$')
);

-- Bank accounts table
CREATE TABLE form_settings_bank_accounts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    bank_name VARCHAR(255) NOT NULL,
    account_name VARCHAR(255) NOT NULL,
    account_number VARCHAR(255) NOT NULL,
    display_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Settings Change History Table

```sql
CREATE TABLE form_settings_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    admin_id INT NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changes JSON NOT NULL,
    FOREIGN KEY (admin_id) REFERENCES admins(id) ON DELETE CASCADE
);
```

**Changes JSON Structure:**

```json
{
  "membershipFee": { "from": 500, "to": 1450 },
  "gcashAccounts": {
    "added": [{ "name": "Juan Dela Cruz", "number": "09171234567" }],
    "removed": [],
    "modified": []
  },
  "bankAccounts": {
    "added": [],
    "removed": [
      {
        "bankName": "BDO",
        "accountName": "Old Account",
        "accountNumber": "1234"
      }
    ],
    "modified": []
  },
  "cashPayment": {
    "openDays": { "from": ["mon", "tue"], "to": ["mon", "tue", "wed"] }
  },
  "successMessage": { "from": "", "to": "Welcome to UPAAC!" }
}
```

---

## Data Types & Validation

### Membership Fee

| Field           | Type            | Required | Validation     | Default |
| --------------- | --------------- | -------- | -------------- | ------- |
| `membershipFee` | `decimal(10,2)` | ✅ Yes   | Min: 0, No max | 1450.00 |

### GCash Account

| Field    | Type     | Required | Validation                              |
| -------- | -------- | -------- | --------------------------------------- |
| `name`   | `string` | ✅ Yes   | Max 255 characters                      |
| `number` | `string` | ✅ Yes   | Exactly 11 digits, must start with `09` |

**Number Format Regex:** `^09[0-9]{9}$`

### Bank Account

| Field           | Type     | Required | Validation         |
| --------------- | -------- | -------- | ------------------ |
| `bankName`      | `string` | ✅ Yes   | Max 255 characters |
| `accountName`   | `string` | ✅ Yes   | Max 255 characters |
| `accountNumber` | `string` | ✅ Yes   | Max 255 characters |

### Cash Payment Details

| Field       | Type       | Required | Validation                                                |
| ----------- | ---------- | -------- | --------------------------------------------------------- |
| `address`   | `string`   | ❌ No    | Max 255 characters                                        |
| `building`  | `string`   | ❌ No    | Max 255 characters                                        |
| `office`    | `string`   | ❌ No    | Max 255 characters                                        |
| `openDays`  | `string[]` | ❌ No    | Array of: `mon`, `tue`, `wed`, `thu`, `fri`, `sat`, `sun` |
| `openHours` | `string`   | ❌ No    | Max 100 characters (e.g., "8:00 AM - 5:00 PM")            |

### Success Message

| Field            | Type     | Required | Validation                     |
| ---------------- | -------- | -------- | ------------------------------ |
| `successMessage` | `string` | ❌ No    | Max 500 characters, plain text |

---

## API Endpoints

### Admin Endpoint (Protected)

**GET/PUT** `/api/admin/settings/form/`

Requires authentication. All admins can access.

#### GET Response

```json
{
  "success": true,
  "data": {
    "settings": {
      "membershipFee": 1450,
      "paymentSettings": {
        "gcashAccounts": [
          { "name": "Juan Dela Cruz", "number": "09171234567" }
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

#### PUT Request Body

```json
{
  "membershipFee": 1450,
  "paymentSettings": {
    "gcashAccounts": [{ "name": "Juan Dela Cruz", "number": "09171234567" }],
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
}
```

#### PUT Response

```json
{
  "success": true,
  "message": "Form settings updated successfully",
  "data": {
    "settings": { ... },
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

#### Error Response

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "membershipFee": "Membership fee must be at least 0",
    "paymentSettings.gcashAccounts[0].number": "Invalid GCash number format. Must be 11 digits starting with 09.",
    "successMessage": "Success message must not exceed 500 characters"
  }
}
```

---

### Public Endpoint (No Auth Required)

**GET** `/api/public/form-settings/`

Returns only the information needed for the registration form. Does NOT include modification history or admin details.

#### Response

```json
{
  "success": true,
  "data": {
    "membershipFee": 1450,
    "paymentMethods": {
      "gcash": {
        "accounts": [{ "name": "Juan Dela Cruz", "number": "09171234567" }]
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

## Activity Log Integration

When form settings are updated, create an activity log entry:

### Activity Log Entry Structure

```json
{
  "action": "form_settings_updated",
  "actionDisplay": "Updated Form Settings",
  "adminId": 1,
  "targetType": "form_settings",
  "targetId": null,
  "notes": "Changed membership fee from Php 500 to Php 1,450. Added 2 GCash accounts. Modified cash payment open days.",
  "ipAddress": "192.168.1.1",
  "timestamp": "2026-01-19T14:35:00Z"
}
```

### Detailed Change Notes Format

The notes should include a human-readable summary of what changed:

- **Membership fee**: "Changed membership fee from Php {old} to Php {new}"
- **GCash accounts**:
  - "Added {n} GCash account(s): {names}"
  - "Removed {n} GCash account(s): {names}"
  - "Modified GCash account: {name}"
- **Bank accounts**:
  - "Added {n} bank account(s): {bank names}"
  - "Removed {n} bank account(s): {bank names}"
  - "Modified bank account: {bank name}"
- **Cash payment**: "Modified cash payment details: {changed fields}"
- **Success message**: "Updated success page message"

---

## Initial Seed Data

```sql
INSERT INTO form_settings (id, membership_fee, gcash_accounts, bank_accounts, cash_payment, success_message)
VALUES (
    1,
    1450.00,
    '[]',
    '[]',
    '{"address": "", "building": "", "office": "", "openDays": [], "openHours": ""}',
    ''
);
```

---

## Frontend TypeScript Types

```typescript
// GCash Account
interface GcashAccount {
  name: string;
  number: string; // 11 digits, format: 09XXXXXXXXX
}

// Bank Account
interface BankAccount {
  bankName: string;
  accountName: string;
  accountNumber: string;
}

// Cash Payment Details
interface CashPaymentDetails {
  address: string;
  building: string;
  office: string;
  openDays: string[]; // ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
  openHours: string;
}

// Payment Settings
interface PaymentSettings {
  gcashAccounts: GcashAccount[];
  bankAccounts: BankAccount[];
  cashPayment: CashPaymentDetails;
}

// Form Settings
interface FormSettings {
  membershipFee: number;
  paymentSettings: PaymentSettings;
  successMessage: string; // max 500 characters
}

// API Response
interface FormSettingsResponse {
  settings: FormSettings;
  lastUpdated?: {
    at: string;
    by: {
      id: number;
      name: string;
      email: string;
    };
  };
}
```

---

## Open Days Reference

| Value | Display Label |
| ----- | ------------- |
| `mon` | Monday        |
| `tue` | Tuesday       |
| `wed` | Wednesday     |
| `thu` | Thursday      |
| `fri` | Friday        |
| `sat` | Saturday      |
| `sun` | Sunday        |
