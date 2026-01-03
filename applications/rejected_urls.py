from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_rejected_applicants, name='list-rejected'),
    path('<int:pk>/', views.get_rejected_applicant_detail, name='rejected-detail'),
    path('export/', views.export_rejected_applicants, name='export-rejected'),
]