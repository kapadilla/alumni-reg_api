from django.urls import path
from . import views

urlpatterns = [
    # Public registration endpoints
    path('submit/', views.submit_registration, name='submit-registration'),
    path('check-email/', views.check_email_availability, name='check-email'),
    
    # Reference Data
    path('reference/provinces/', views.list_provinces, name='list-provinces'),
    path('reference/cities/', views.list_cities, name='list-cities'),
    path('reference/barangays/', views.list_barangays, name='list-barangays'),
    path('reference/degree-programs/', views.list_degree_programs, name='list-degree-programs'),
]