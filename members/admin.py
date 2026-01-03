from django.contrib import admin
from .models import Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'member_since', 'is_active']
    list_filter = ['is_active', 'member_since']
    search_fields = ['full_name', 'email']
    readonly_fields = ['member_since']