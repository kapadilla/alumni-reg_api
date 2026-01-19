from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, EmailValidator

# ============================================
# MAIN APPLICATION MODEL
# ============================================


class MembershipApplication(models.Model):
    STATUS_CHOICES = [
        ("pending_alumni_verification", "Pending Alumni Verification"),
        ("pending_payment_verification", "Pending Payment Verification"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("revoked", "Revoked"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("gcash", "GCash"),
        ("bank", "Bank Transfer"),
        ("cash", "Cash"),
    ]

    REJECTION_STAGE_CHOICES = [
        ("alumni_verification", "Alumni Verification"),
        ("payment_verification", "Payment Verification"),
    ]

    MENTORSHIP_FORMAT_CHOICES = [
        ("one-on-one", "1-on-1 Mentorship"),
        ("group", "Group Mentorship"),
        ("both", "Either format works"),
    ]

    # ===== PERSONAL DETAILS =====
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100)
    suffix = models.CharField(max_length=20, blank=True, null=True)
    maiden_name = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField()

    # Contact Information
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    mobile_number = models.CharField(
        max_length=13,
        validators=[
            RegexValidator(
                regex=r"^(09|\+639)\d{9}$", message="Invalid PH mobile number"
            )
        ],
    )

    # Address (stored as text - frontend uses external API for lookups)
    current_address = models.CharField(max_length=255)
    province = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    barangay = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=4, null=True, blank=True)

    # ===== ACADEMIC STATUS =====
    degree_program = models.CharField(max_length=200)
    campus = models.CharField(max_length=200, default="UP Cebu")
    year_graduated = models.CharField(
        max_length=4,
        null=True,
        blank=True,
        validators=[RegexValidator(regex=r"^\d{4}$", message="Year must be 4 digits")],
    )
    student_number = models.CharField(max_length=20, blank=True, null=True)

    # ===== PROFESSIONAL INFORMATION =====
    current_employer = models.CharField(max_length=200, blank=True, null=True)
    job_title = models.CharField(max_length=100, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    years_of_experience = models.IntegerField(null=True, blank=True)

    # ===== MEMBERSHIP & PAYMENT =====
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES, default="gcash"
    )
    gcash_reference_number = models.CharField(max_length=50, null=True, blank=True)
    gcash_proof_of_payment = models.FileField(
        upload_to="payment/gcash/", null=True, blank=True
    )
    bank_sender_name = models.CharField(max_length=255, null=True, blank=True)
    bank_name = models.CharField(max_length=100, null=True, blank=True)
    bank_account_number = models.CharField(max_length=4, null=True, blank=True)
    bank_reference_number = models.CharField(max_length=100, null=True, blank=True)
    bank_proof_of_payment = models.FileField(
        upload_to="payment/bank/", null=True, blank=True
    )
    cash_payment_date = models.DateField(null=True, blank=True)
    cash_received_by = models.CharField(max_length=255, null=True, blank=True)
    payment_notes = models.TextField(null=True, blank=True)

    # ===== MENTORSHIP PROGRAM =====
    join_mentorship_program = models.BooleanField(default=False)
    mentorship_areas = models.JSONField(null=True, blank=True, default=list)
    mentorship_areas_other = models.TextField(null=True, blank=True)
    mentorship_industry_tracks = models.JSONField(null=True, blank=True, default=list)
    mentorship_industry_tracks_other = models.TextField(null=True, blank=True)
    mentorship_format = models.CharField(
        max_length=50, null=True, blank=True, choices=MENTORSHIP_FORMAT_CHOICES
    )
    mentorship_availability = models.IntegerField(
        null=True, blank=True, help_text="Hours per month"
    )

    # ===== STATUS TRACKING =====
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="pending_alumni_verification",
        db_index=True,
    )
    date_applied = models.DateTimeField(auto_now_add=True, db_index=True)

    # Alumni Verification (Step 1)
    alumni_verified_at = models.DateTimeField(null=True, blank=True)
    alumni_verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alumni_verified_applications",
    )

    # Payment Verification / Approval (Step 2)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_applications",
    )

    # Rejection
    rejected_at = models.DateTimeField(null=True, blank=True)
    rejected_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rejected_applications",
    )
    rejection_stage = models.CharField(
        max_length=30, choices=REJECTION_STAGE_CHOICES, null=True, blank=True
    )
    rejection_reason = models.TextField(null=True, blank=True)

    # Admin Notes
    # admin_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-date_applied"]
        db_table = "membership_applications"
        indexes = [
            models.Index(fields=["status", "date_applied"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.status}"

    @property
    def full_name(self):
        suffix = f" {self.suffix}" if self.suffix else ""
        return f"{self.first_name} {self.last_name}{suffix}"


# ============================================
# VERIFICATION HISTORY (AUDIT TRAIL)
# ============================================


class VerificationHistory(models.Model):
    ACTION_CHOICES = [
        ("submitted", "Application Submitted"),
        ("alumni_verified", "Alumni Verified"),
        ("payment_confirmed", "Payment Confirmed"),
        ("rejected", "Application Rejected"),
        ("membership_revoked", "Membership Revoked"),
        ("membership_reinstated", "Membership Reinstated"),
    ]

    application = models.ForeignKey(
        MembershipApplication,
        on_delete=models.CASCADE,
        related_name="verification_history",
    )
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    performed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        db_table = "verification_history"
        verbose_name_plural = "Verification histories"

    def __str__(self):
        return f"{self.application.full_name} - {self.action}"
