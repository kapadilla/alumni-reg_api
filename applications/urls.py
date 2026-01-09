from django.urls import path
from . import views

urlpatterns = [
    # Public registration endpoints
    path('submit/', views.submit_registration, name='submit-registration'),
    path('check-email/', views.check_email_availability, name='check-email'),
    
    # Reference Data (degree programs only - address data from external API)
    path('reference/degree-programs/', views.list_degree_programs, name='list-degree-programs'),
]