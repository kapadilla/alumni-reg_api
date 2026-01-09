from django.db import models
from django.contrib.auth.models import User
from applications.models import MembershipApplication


class Member(models.Model):
    application = models.OneToOneField(
        MembershipApplication,
        on_delete=models.CASCADE,
        related_name='member_profile'
    )
    member_since = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    # For quick access (denormalized from application)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    
    # Revocation tracking
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='member_revocations'
    )
    revocation_reason = models.TextField(blank=True)
    
    # Reinstatement tracking
    reinstated_at = models.DateTimeField(null=True, blank=True)
    reinstated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='member_reinstatements'
    )
    
    class Meta:
        ordering = ['-member_since']
        db_table = 'members'
    
    def __str__(self):
        return self.full_name
    
    def save(self, *args, **kwargs):
        # Auto-populate denormalized fields
        if not self.full_name:
            self.full_name = self.application.full_name
        if not self.email:
            self.email = self.application.email
        super().save(*args, **kwargs)