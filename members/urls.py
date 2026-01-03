from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_members, name='list-members'),
    path('<int:pk>/', views.get_member_detail, name='member-detail'),
    path('<int:pk>/update/', views.update_member, name='update-member'),
    path('<int:pk>/revoke/', views.revoke_membership, name='revoke-membership'),
    path('export/', views.export_members, name='export-members'),
]