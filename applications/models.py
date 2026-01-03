from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, EmailValidator


# ============================================
# REFERENCE DATA MODELS 
# ============================================

class Province(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    class Meta:
        ordering = ['name']
        db_table = 'provinces'
    
    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=100)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='cities')
    
    class Meta:
        ordering = ['name']
        db_table = 'cities'
        verbose_name_plural = 'Cities'
        unique_together = ['name', 'province']  # Same city name can exist in different provinces
    
    def __str__(self):
        return f"{self.name}, {self.province.name}"


class Barangay(models.Model):
    name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='barangays')
    
    class Meta:
        ordering = ['name']
        db_table = 'barangays'
        unique_together = ['name', 'city']  # Same barangay name can exist in different cities
    
    def __str__(self):
        return f"{self.name}, {self.city.name}"


class DegreeProgram(models.Model):
    name = models.CharField(max_length=200, unique=True)
    college = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
        db_table = 'degree_programs'
    
    def __str__(self):
        return self.name


# ============================================
# MAIN APPLICATION MODEL
# ============================================

class MembershipApplication(models.Model):
    TITLE_CHOICES = [
        ('Mr', 'Mr.'),
        ('Ms', 'Ms.'),
        ('Mrs', 'Mrs.'),
        ('Dr', 'Dr.'),
    ]
    
    STATUS_CHOICES = [
        ('pending_alumni_verification', 'Pending Alumni Verification'),
        ('pending_payment_verification', 'Pending Payment Verification'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('gcash', 'GCash'),
        ('bank', 'Bank Transfer'),
        ('cash', 'Cash'),
    ]
    
    REJECTION_STAGE_CHOICES = [
        ('alumni_verification', 'Alumni Verification'),
        ('payment_verification', 'Payment Verification'),
    ]
    
    # ===== PERSONAL DETAILS =====
    title = models.CharField(max_length=10, choices=TITLE_CHOICES)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    suffix = models.CharField(max_length=20, blank=True, null=True)
    maiden_name = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField()
    
    # Contact Information
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    mobile_number = models.CharField(
        max_length=13,
        validators=[RegexValidator(regex=r'^(09|\+639)\d{9}$', message='Invalid PH mobile number')]
    )
    
    # Address (now using names directly)
    current_address = models.CharField(max_length=255)
    province = models.ForeignKey(Province, on_delete=models.PROTECT)
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    barangay = models.ForeignKey(Barangay, on_delete=models.PROTECT)
    
    # ===== ACADEMIC STATUS =====
    degree_program = models.ForeignKey(DegreeProgram, on_delete=models.PROTECT)
    year_graduated = models.CharField(max_length=4, validators=[
        RegexValidator(regex=r'^\d{4}$', message='Year must be 4 digits')
    ])
    student_number = models.CharField(max_length=20, blank=True, null=True)
    
    # ===== PROFESSIONAL INFORMATION =====
    current_employer = models.CharField(max_length=200, blank=True, null=True)
    job_title = models.CharField(max_length=100, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    
    # ===== MEMBERSHIP =====
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    
    # ===== STATUS TRACKING =====
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='pending_alumni_verification',
        db_index=True
    )
    date_applied = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Alumni Verification (Step 1)
    alumni_verified_at = models.DateTimeField(null=True, blank=True)
    alumni_verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alumni_verifications'
    )
    
    # Payment Verification / Approval (Step 2)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='application_approvals'
    )
    
    # Rejection
    rejected_at = models.DateTimeField(null=True, blank=True)
    rejected_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='application_rejections'
    )
    rejection_stage = models.CharField(
        max_length=30,
        choices=REJECTION_STAGE_CHOICES,
        null=True,
        blank=True
    )
    rejection_reason = models.TextField(null=True, blank=True)
    
    # Admin Notes
    admin_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-date_applied']
        db_table = 'membership_applications'
        indexes = [
            models.Index(fields=['status', 'date_applied']),
            models.Index(fields=['email']),
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
        ('submitted', 'Application Submitted'),
        ('alumni_verified', 'Alumni Verified'),
        ('payment_confirmed', 'Payment Confirmed'),
        ('rejected', 'Application Rejected'),
    ]
    
    application = models.ForeignKey(
        MembershipApplication,
        on_delete=models.CASCADE,
        related_name='history'
    )
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        db_table = 'verification_history'
        verbose_name_plural = 'Verification histories'
    
    def __str__(self):
        return f"{self.application.full_name} - {self.action}"