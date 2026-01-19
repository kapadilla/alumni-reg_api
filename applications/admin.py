from django.contrib import admin
from .models import (
    MembershipApplication, VerificationHistory
)


@admin.register(MembershipApplication)
class MembershipApplicationAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'status', 'date_applied']
    list_filter = ['status', 'date_applied', 'degree_program']
    search_fields = ['first_name', 'last_name', 'email']
    readonly_fields = ['date_applied']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'middle_name', 'last_name', 'suffix', 'maiden_name', 'date_of_birth')
        }),
        ('Contact Information', {
            'fields': ('email', 'mobile_number', 'current_address', 'province', 'city', 'barangay')
        }),
        ('Academic Information', {
            'fields': ('degree_program', 'campus', 'year_graduated', 'student_number')
        }),
        ('Professional Information', {
            'fields': ('current_employer', 'job_title', 'industry')
        }),
        ('Membership', {
            'fields': ('payment_method',)
        }),
        ('Status', {
            'fields': ('status', 'date_applied')
        }),
        ('Verification Details', {
            'fields': (
                'alumni_verified_at', 'alumni_verified_by',
                'approved_at', 'approved_by',
                'rejected_at', 'rejected_by', 'rejection_stage', 'rejection_reason'
            )
        }),
    )


@admin.register(VerificationHistory)
class VerificationHistoryAdmin(admin.ModelAdmin):
    list_display = ['application', 'action', 'performed_by', 'timestamp']
    list_filter = ['action', 'timestamp']
    readonly_fields = ['timestamp']