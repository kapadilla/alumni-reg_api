# Registration Form Fields Reference

Reference for backend endpoint and database schema design.

---

## Personal Information

| Field         | Type     | Required | Notes               |
| ------------- | -------- | -------- | ------------------- |
| `firstName`   | `string` | ✅ Yes   | Min 2 characters    |
| `lastName`    | `string` | ✅ Yes   | Min 2 characters    |
| `middleName`  | `string` | ❌ No    |                     |
| `suffix`      | `string` | ❌ No    | e.g., Jr., Sr., III |
| `maidenName`  | `string` | ❌ No    |                     |
| `dateOfBirth` | `date`   | ✅ Yes   | ISO date format     |

---

## Contact & Location

| Field            | Type     | Required | Notes                             |
| ---------------- | -------- | -------- | --------------------------------- |
| `email`          | `string` | ✅ Yes   | Valid email format                |
| `mobileNumber`   | `string` | ✅ Yes   | Format: `09XXXXXXXXX` (11 digits) |
| `currentAddress` | `string` | ✅ Yes   |                                   |
| `province`       | `string` | ✅ Yes   |                                   |
| `city`           | `string` | ✅ Yes   |                                   |
| `barangay`       | `string` | ✅ Yes   |                                   |
| `zipCode`        | `string` | ✅ Yes   | Exactly 4 digits                  |

---

## Academic Status

| Field           | Type     | Required | Notes                              |
| --------------- | -------- | -------- | ---------------------------------- |
| `degreeProgram` | `string` | ✅ Yes   |                                    |
| `campus`        | `string` | ✅ Yes   | Default: "UP Cebu"                 |
| `yearGraduated` | `string` | ❌ No    | 4-digit year (1970 - current year) |
| `studentNumber` | `string` | ❌ No    |                                    |

---

## Professional Information

| Field               | Type     | Required | Notes         |
| ------------------- | -------- | -------- | ------------- |
| `currentEmployer`   | `string` | ❌ No    |               |
| `industry`          | `string` | ❌ No    |               |
| `jobTitle`          | `string` | ❌ No    |               |
| `yearsOfExperience` | `string` | ❌ No    | Numeric value |

---

## Mentorship Program

| Field                           | Type       | Required       | Condition                                                 |
| ------------------------------- | ---------- | -------------- | --------------------------------------------------------- |
| `joinMentorshipProgram`         | `boolean`  | ❌ No          | Default: `false`                                          |
| `mentorshipAreas`               | `string[]` | ⚠️ Conditional | Required if `joinMentorshipProgram` is `true`             |
| `mentorshipAreasOther`          | `string`   | ⚠️ Conditional | Required if `mentorshipAreas` includes `"other"`          |
| `mentorshipIndustryTracks`      | `string[]` | ⚠️ Conditional | Required if `joinMentorshipProgram` is `true`             |
| `mentorshipIndustryTracksOther` | `string`   | ⚠️ Conditional | Required if `mentorshipIndustryTracks` includes `"other"` |
| `mentorshipFormat`              | `string`   | ⚠️ Conditional | Required if `joinMentorshipProgram` is `true`             |
| `mentorshipAvailability`        | `string`   | ⚠️ Conditional | Required if `joinMentorshipProgram` is `true`             |

### Mentorship Option Values

**mentorshipAreas**: `career-advancement`, `leadership-management`, `business-corporate`, `finance-operations`, `technology-innovation`, `hr-workplace`, `entrepreneurship`, `other`

**mentorshipIndustryTracks**: `it-software`, `banking-finance`, `marketing-advertising`, `engineering`, `healthcare`, `real-estate`, `supply-chain`, `government-public`, `other`

**mentorshipFormat**: `one-on-one`, `group`, `both`

---

## Membership Payment

| Field                  | Type     | Required       | Condition                                               |
| ---------------------- | -------- | -------------- | ------------------------------------------------------- |
| `paymentMethod`        | `string` | ✅ Yes         | Values: `gcash`, `bank`, `cash`                         |
| `gcashReferenceNumber` | `string` | ⚠️ Conditional | Required if `paymentMethod` is `"gcash"`                |
| `gcashProofOfPayment`  | `File`   | ⚠️ Conditional | Required if `paymentMethod` is `"gcash"`                |
| `bankSenderName`       | `string` | ⚠️ Conditional | Required if `paymentMethod` is `"bank"`                 |
| `bankName`             | `string` | ⚠️ Conditional | Required if `paymentMethod` is `"bank"`                 |
| `bankAccountNumber`    | `string` | ⚠️ Conditional | Required if `paymentMethod` is `"bank"` (last 4 digits) |
| `bankReferenceNumber`  | `string` | ⚠️ Conditional | Required if `paymentMethod` is `"bank"`                 |
| `bankProofOfPayment`   | `File`   | ⚠️ Conditional | Required if `paymentMethod` is `"bank"`                 |
| `cashPaymentDate`      | `date`   | ⚠️ Conditional | Required if `paymentMethod` is `"cash"`                 |
| `cashReceivedBy`       | `string` | ⚠️ Conditional | Required if `paymentMethod` is `"cash"`                 |
| `paymentNotes`         | `string` | ❌ No          |                                                         |

---

## Data Privacy

| Field                | Type      | Required | Notes                                                       |
| -------------------- | --------- | -------- | ----------------------------------------------------------- |
| `dataPrivacyConsent` | `boolean` | ✅ Yes   | Must be `true` (frontend validation only, not stored in DB) |

---

## Summary

| Category                 | Required          | Optional | Conditional |
| ------------------------ | ----------------- | -------- | ----------- |
| Personal Information     | 3                 | 3        | 0           |
| Contact & Location       | 7                 | 0        | 0           |
| Academic Status          | 1                 | 2        | 0           |
| Professional Information | 0                 | 4        | 0           |
| Mentorship Program       | 0                 | 1        | 6           |
| Membership Payment       | 1                 | 1        | 10          |
| Data Privacy             | 1 (frontend only) | 0        | 0           |
| **Total**                | **13**            | **11**   | **16**      |
