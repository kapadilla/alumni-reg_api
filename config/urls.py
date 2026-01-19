"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from form_settings.urls import admin_urlpatterns as form_settings_admin_urls
from form_settings.urls import public_urlpatterns as form_settings_public_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    # API v1 endpoints
    path("api/v1/auth/", include("accounts.urls")),
    path("api/v1/registration/", include("applications.urls")),
    path("api/v1/verification/", include("applications.verification_urls")),
    path("api/v1/rejected/", include("applications.rejected_urls")),
    path("api/v1/members/", include("members.urls")),
    path("api/v1/dashboard/", include("applications.dashboard_urls")),
    # Form settings endpoints
    path("api/v1/admin/settings/", include(form_settings_admin_urls)),
    path("api/v1/public/", include(form_settings_public_urls)),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
