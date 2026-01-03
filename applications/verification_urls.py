from django.urls import path
from . import views

urlpatterns = [
    # Alumni Verification (Step 1)
    path('alumni/', views.list_pending_alumni_verification, name='list-alumni-verification'),
    path('alumni/<int:pk>/', views.get_alumni_verification_detail, name='alumni-verification-detail'),
    path('alumni/<int:pk>/verify/', views.verify_alumni, name='verify-alumni'),
    path('alumni/<int:pk>/reject/', views.reject_alumni_verification, name='reject-alumni'),
    path('alumni/export/', views.export_alumni_verification, name='export-alumni-verification'),
    
    # Payment Verification (Step 2)
    path('payment/', views.list_pending_payment_verification, name='list-payment-verification'),
    path('payment/<int:pk>/', views.get_payment_verification_detail, name='payment-verification-detail'),
    path('payment/<int:pk>/confirm/', views.confirm_payment, name='confirm-payment'),
    path('payment/<int:pk>/reject/', views.reject_payment_verification, name='reject-payment'),
    path('payment/export/', views.export_payment_verification, name='export-payment-verification'),
]