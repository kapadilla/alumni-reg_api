from django.urls import path
from . import views

urlpatterns = [
    # Public registration endpoints
    path('submit/', views.submit_registration, name='submit-registration'),
    path('check-email/', views.check_email_availability, name='check-email'),
]