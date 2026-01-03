from django.urls import path
from . import views

urlpatterns = [
    # Registration
    path('submit/', views.submit_registration, name='submit-registration'),
    path('check-email/', views.check_email_availability, name='check-email'),
    
    # Alumni Verification (Step 1)
    path('verification/alumni/', views.list_pending_alumni_verification, name='list-alumni-verification'),
    path('verification/alumni/<int:pk>/', views.get_alumni_verification_detail, name='alumni-verification-detail'),
    path('verification/alumni/<int:pk>/verify/', views.verify_alumni, name='verify-alumni'),
    path('verification/alumni/<int:pk>/reject/', views.reject_alumni_verification, name='reject-alumni'),
    path('verification/alumni/export/', views.export_alumni_verification, name='export-alumni-verification'),
    
    # Payment Verification (Step 2)
    path('verification/payment/', views.list_pending_payment_verification, name='list-payment-verification'),
    path('verification/payment/<int:pk>/', views.get_payment_verification_detail, name='payment-verification-detail'),
    path('verification/payment/<int:pk>/confirm/', views.confirm_payment, name='confirm-payment'),
    path('verification/payment/<int:pk>/reject/', views.reject_payment_verification, name='reject-payment'),
    path('verification/payment/export/', views.export_payment_verification, name='export-payment-verification'),
    
    # Rejected Applicants
    path('rejected/', views.list_rejected_applicants, name='list-rejected'),
    path('rejected/<int:pk>/', views.get_rejected_applicant_detail, name='rejected-detail'),
    path('rejected/export/', views.export_rejected_applicants, name='export-rejected'),
    
    # Dashboard
    path('dashboard/stats/', views.dashboard_stats, name='dashboard-stats'),
    path('dashboard/activity/', views.dashboard_activity, name='dashboard-activity'),
    
    # Reference Data
    path('reference/provinces/', views.list_provinces, name='list-provinces'),
    path('reference/cities/', views.list_cities, name='list-cities'),
    path('reference/barangays/', views.list_barangays, name='list-barangays'),
    path('reference/degree-programs/', views.list_degree_programs, name='list-degree-programs'),
]