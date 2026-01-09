from django_filters import rest_framework as filters
from .models import AdminActivityLog


class AdminActivityLogFilter(filters.FilterSet):
    """Filter for admin activity logs"""
    
    date_from = filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    date_to = filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')
    action = filters.ChoiceFilter(choices=AdminActivityLog.ACTION_CHOICES)
    target_type = filters.ChoiceFilter(choices=AdminActivityLog.TARGET_TYPE_CHOICES)
    
    class Meta:
        model = AdminActivityLog
        fields = ['date_from', 'date_to', 'action', 'target_type']
