from django.db import models
from django.contrib.auth.models import User


class AdminActivityLog(models.Model):
    """Track all admin activities for audit trail and activity log"""
    
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('verify_alumni', 'Verified Alumni'),
        ('reject_alumni', 'Rejected Alumni Verification'),
        ('approve_member', 'Approved Member'),
        ('reject_payment', 'Rejected Payment Verification'),
        ('revoke_member', 'Revoked Membership'),
        ('reinstate_member', 'Reinstated Membership'),
        ('deactivate_admin', 'Deactivated Admin'),
        ('reactivate_admin', 'Reactivated Admin'),
    ]
    
    TARGET_TYPE_CHOICES = [
        ('application', 'Application'),
        ('member', 'Member'),
        ('admin', 'Admin User'),
    ]
    
    admin = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activity_logs'
    )
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Optional target information (for actions on specific entities)
    target_type = models.CharField(
        max_length=20,
        choices=TARGET_TYPE_CHOICES,
        null=True,
        blank=True
    )
    target_id = models.IntegerField(null=True, blank=True)
    target_name = models.CharField(max_length=200, blank=True)  # Denormalized for quick access
    
    # Additional context
    notes = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        db_table = 'admin_activity_logs'
        indexes = [
            models.Index(fields=['admin', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.admin.email} - {self.get_action_display()} - {self.timestamp}"
