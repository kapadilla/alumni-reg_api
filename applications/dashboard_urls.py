from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.dashboard_stats, name='dashboard-stats'),
    path('activity/', views.dashboard_activity, name='dashboard-activity'),
    path('filters/', views.filter_options, name='filter-options'),
]