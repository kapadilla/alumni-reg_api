from django.urls import path
from . import views

# Admin URL patterns - to be included under /api/v1/admin/settings/
admin_urlpatterns = [
    path("form/", views.admin_form_settings, name="admin-form-settings"),
]

# Public URL patterns - to be included under /api/v1/public/
public_urlpatterns = [
    path("form-settings/", views.public_form_settings, name="public-form-settings"),
]
