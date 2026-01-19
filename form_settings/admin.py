from django.contrib import admin
from .models import FormSettings, FormSettingsHistory


@admin.register(FormSettings)
class FormSettingsAdmin(admin.ModelAdmin):
    list_display = ("id", "membership_fee", "updated_at", "updated_by")
    readonly_fields = ("id", "updated_at")

    def has_add_permission(self, request):
        # Prevent creating additional instances (singleton pattern)
        return not FormSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the singleton
        return False


@admin.register(FormSettingsHistory)
class FormSettingsHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "admin", "changed_at")
    list_filter = ("admin", "changed_at")
    readonly_fields = ("admin", "changed_at", "changes")
    ordering = ("-changed_at",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
