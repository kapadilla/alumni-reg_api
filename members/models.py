from django.db import models
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