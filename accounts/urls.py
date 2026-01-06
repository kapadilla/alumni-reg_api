from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify/', views.verify_token, name='verify-token'),
    # Admin Management
    path('admins/', views.admin_list_create, name='admin-list-create'),
    path('admins/<int:pk>/', views.admin_detail, name='admin-detail'),
]