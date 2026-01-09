from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify/', views.verify_token, name='verify-token'),
    # Admin Management
    path('admins/', views.admin_list_create, name='admin-list-create'),
    path('admins/<int:pk>/', views.admin_detail, name='admin-detail'),
    path('admins/<int:pk>/reactivate/', views.reactivate_admin, name='admin-reactivate'),
    path('admins/<int:pk>/activity/', views.admin_activity_log, name='admin-activity-log'),
]